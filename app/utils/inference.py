import torch
import os
import logging
from time import strftime
from app.utils.src.utils.preprocess import CropAndExtract
from app.utils.src.test_audio2coeff import Audio2Coeff
from app.utils.src.facerender.animate import AnimateFromCoeff
from app.utils.src.generate_batch import get_data
from app.utils.src.generate_facerender_batch import get_facerender_data
from app.utils.third_part.GFPGAN.gfpgan import GFPGANer
from app.utils.third_part.GPEN.gpen_face_enhancer import FaceEnhancement
from app.models import SyncTask
import warnings
import os
from syncMate.settings import BASE_DIR

# Suppress warnings
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)

CHECKPOINT_DIR = os.path.join(BASE_DIR, 'checkpoints')
CHECKPOINT_DAIN_DIR = os.path.join(BASE_DIR, 'checkpoints/DAIN_weight')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
DAIN_RESULTS_DIR = os.path.join(BASE_DIR, 'results/dian_output')

class VideoProcessor:
    def __init__(self, 
                 task_id,
                 checkpoint_dir=CHECKPOINT_DIR,
                 result_dir=RESULTS_DIR,
                 batch_size=1,
                 enhancer='lip',
                 use_cuda=True,
                 use_DAIN=True,
                 DAIN_weight=CHECKPOINT_DAIN_DIR,
                 dian_output='dian_output',
                 time_step=0.5,
                 remove_duplicates=False):
        self.task_id = task_id
        task = SyncTask.objects.get(task_id=task_id)
        self.driven_audio = task.audio_file.path
        self.source_video = task.video_file.path
        self.checkpoint_dir = checkpoint_dir
        self.result_dir = result_dir
        self.batch_size = batch_size
        self.enhancer = enhancer

        # Check if CUDA is available and user wants to use it
        self.device = "cuda" if torch.cuda.is_available() and use_cuda else "cpu"

        # DAIN related args
        self.use_DAIN = use_DAIN
        self.DAIN_weight = DAIN_weight
        self.dian_output = dian_output
        self.time_step = time_step
        self.remove_duplicates = remove_duplicates

    def preprocess(self):
        logging.info("Initializing models for preprocessing.")
        current_code_path = os.path.realpath(__file__)
        current_root_path = os.path.split(current_code_path)[0]
        os.environ['TORCH_HOME'] = os.path.join(current_root_path, self.checkpoint_dir)

        # Model paths
        path_of_lm_croper = os.path.join(current_root_path, self.checkpoint_dir, 'shape_predictor_68_face_landmarks.dat')
        path_of_net_recon_model = os.path.join(current_root_path, self.checkpoint_dir, 'epoch_20.pth')
        dir_of_BFM_fitting = os.path.join(current_root_path, self.checkpoint_dir, 'BFM_Fitting')
        
        # Initializing preprocessing model
        preprocess_model = CropAndExtract(path_of_lm_croper, path_of_net_recon_model, dir_of_BFM_fitting, self.device)
        return preprocess_model

    def audio_to_coefficient(self):
        logging.info("Initializing audio to coefficient model.")
        current_code_path = os.path.realpath(__file__)
        current_root_path = os.path.split(current_code_path)[0]
        
        # Model paths
        audio2pose_checkpoint = os.path.join(current_root_path, self.checkpoint_dir, 'auido2pose_00140-model.pth')
        audio2pose_yaml_path = os.path.join(current_root_path, 'src', 'config', 'auido2pose.yaml')
        audio2exp_checkpoint = os.path.join(current_root_path, self.checkpoint_dir, 'auido2exp_00300-model.pth')
        audio2exp_yaml_path = os.path.join(current_root_path, 'src', 'config', 'auido2exp.yaml')
        wav2lip_checkpoint = os.path.join(current_root_path, self.checkpoint_dir, 'wav2lip.pth')
        
        # Initializing audio to coefficient model
        audio_to_coeff = Audio2Coeff(audio2pose_checkpoint, audio2pose_yaml_path, audio2exp_checkpoint, audio2exp_yaml_path,
                                     wav2lip_checkpoint, self.device)
        return audio_to_coeff

    def animate(self):
        logging.info("Initializing animation model.")
        current_code_path = os.path.realpath(__file__)
        current_root_path = os.path.split(current_code_path)[0]
        
        # Model paths
        free_view_checkpoint = os.path.join(current_root_path, self.checkpoint_dir, 'facevid2vid_00189-model.pth.tar')
        mapping_checkpoint = os.path.join(current_root_path, self.checkpoint_dir, 'mapping_00109-model.pth.tar')
        facerender_yaml_path = os.path.join(current_root_path, 'src', 'config', 'facerender_still.yaml')
        
        # Initializing animation model
        animate_from_coeff = AnimateFromCoeff(free_view_checkpoint, mapping_checkpoint, facerender_yaml_path, self.device)
        return animate_from_coeff

    def main(self):
        torch.cuda.empty_cache()

        save_dir = os.path.join(self.result_dir, strftime("%Y_%m_%d_%H.%M.%S"))
        os.makedirs(save_dir, exist_ok=True)

        try:
            task = SyncTask.objects.get(task_id=self.task_id)
            # Preprocessing
            preprocess_model = self.preprocess()
            first_frame_dir = os.path.join(save_dir, 'first_frame_dir')
            os.makedirs(first_frame_dir, exist_ok=True)
            logging.info('3DMM Extraction for source image.')
            print(self.source_video)
            first_coeff_path, crop_pic_path, crop_info = preprocess_model.generate(self.source_video, first_frame_dir)
            if first_coeff_path is None:
                logging.error("Can't get the coefficients of the input.")
                return

            # Audio to Coeff
            audio_to_coeff = self.audio_to_coefficient()
            batch = get_data(first_coeff_path, self.driven_audio, self.device)
            coeff_path = audio_to_coeff.generate(batch, save_dir)
            # Animate
            restorer_model = GFPGANer(model_path='checkpoints/GFPGANv1.3.pth', upscale=1, arch='clean',channel_multiplier=2, bg_upsampler=None)
            enhancer_model = FaceEnhancement(base_dir='checkpoints', size=512, model='GPEN-BFR-512', use_sr=False,sr_model='rrdb_realesrnet_psnr', channel_multiplier=2, narrow=1, device=self.device)
            animate_from_coeff = self.animate()
            data = get_facerender_data(coeff_path, crop_pic_path, first_coeff_path, self.driven_audio, self.batch_size, self.device)
            tmp_path, new_audio_path, return_path = animate_from_coeff.generate(data, save_dir, self.source_video, crop_info,restorer_model, enhancer_model, self.enhancer)
            print('temp_path--------- {}'.format(tmp_path))
            print('return_path--------- {}'.format(return_path))
            print('new_audio_path--------- {}'.format(new_audio_path))
            task.synced_file_path = return_path
            task.status = SyncTask.finished
            task.save()
            torch.cuda.empty_cache()
            os.remove(tmp_path)
            return True

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            task = SyncTask.objects.get(task_id=self.task_id)
            task.status = SyncTask.failed
            task.save()
            raise e

if __name__ == '__main__':
    # Example usage
    processor =  VideoProcessor()
    processor.main()
