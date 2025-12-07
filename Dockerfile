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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# 2. Create working directory
# ----------------------------------------------------------
WORKDIR /app

# ----------------------------------------------------------
# 3. Copy requirements
# ----------------------------------------------------------
COPY requirements.txt .

# ----------------------------------------------------------
# 4. Install Python dependencies
# ----------------------------------------------------------
# Install PyTorch CPU from official wheel URL (small + stable)
RUN pip install --no-cache-dir torch==2.0.1+cpu torchvision==0.15.2+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Now install the rest
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------
# 5. Copy the app code
# ----------------------------------------------------------
COPY . .

# ----------------------------------------------------------
# 6. Expose port
# ----------------------------------------------------------
EXPOSE 8000

# ----------------------------------------------------------
# 7. Start FastAPI
# ----------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
