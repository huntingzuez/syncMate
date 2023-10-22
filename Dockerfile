# Pull base image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONOPTIMIZE=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VENV_PATH /syncmate/venv

# Copy the requirements file
COPY requirements.txt /tmp

# Change the working directory
WORKDIR /syncmate

# Copy the entire project directory contents
COPY . /syncmate

# Update system packages, install ffmpeg, unzip utility, and pip packages
RUN apt-get update && \
    apt-get install -y ffmpeg unzip && \
    # Update pip
    pip install --upgrade pip && \
    # Install specific torch packages with the extra index url
    pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113 && \
    python -m pip install paddlepaddle-gpu==2.3.2.post112 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html && \
    # Install pip packages from requirements.txt
    pip install --no-cache-dir -r /tmp/requirements.txt 

