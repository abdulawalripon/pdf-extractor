FROM python:3.10-slim

# ----------------------------------------------------------
# 1. Install system dependencies
# ----------------------------------------------------------
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-ben \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# 2. Working directory
# ----------------------------------------------------------
WORKDIR /app

# ----------------------------------------------------------
# 3. Copy requirements
# ----------------------------------------------------------
COPY requirements.txt .

# ----------------------------------------------------------
# 4. Install PyTorch (CPU only)
# ----------------------------------------------------------
RUN pip install --no-cache-dir torch==2.0.1+cpu torchvision==0.15.2+cpu -f https://download.pytorch.org/whl/torch_stable.html

# ----------------------------------------------------------
# 5. Install remaining dependencies
# ----------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------
# 6. Download EasyOCR models inside Docker
# ----------------------------------------------------------
RUN mkdir -p /root/.EasyOCR
RUN wget -O /root/.EasyOCR/craft_mlt_25k.pth https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/craft_mlt_25k.pth
RUN wget -O /root/.EasyOCR/vgg_transformer.pth https://github.com/JaidedAI/EasyOCR/releases/download/v1.6/vgg_transformer.pth

# Bangla model folder
RUN mkdir -p /root/.EasyOCR/lang_char
RUN wget -O /root/.EasyOCR/lang_char/bn_g2.pth https://github.com/JaidedAI/EasyOCR/releases/download/v1.6/bn_g2.pth

# ----------------------------------------------------------
# 7. Copy application files
# ----------------------------------------------------------
COPY . .

# ----------------------------------------------------------
# 8. Expose API port
# ----------------------------------------------------------
EXPOSE 8000

# ----------------------------------------------------------
# 9. Start FastAPI app
# ----------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
