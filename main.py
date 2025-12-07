import io
import base64
import numpy as np
import cv2
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# PDF libraries
import pdfplumber
from pdf2image import convert_from_bytes

# OCR
import easyocr

# Image processing
from PIL import Image

# ----------------------------------------------------------
# Load EasyOCR models (Railway-compatible offline loading)
# ----------------------------------------------------------
reader = easyocr.Reader(
    ['bn', 'en'],
    gpu=False,
    model_storage_directory="/root/.EasyOCR",
    user_network_directory="/root/.EasyOCR",
    download_enabled=False
)

# ----------------------------------------------------------
# FastAPI Application
# ----------------------------------------------------------
app = FastAPI(title="PDF Extractor API (PDFPlumber + EasyOCR)")


# ----------------------------------------------------------
# 1️⃣ NORMAL PDF EXTRACTION (no OCR)
# ----------------------------------------------------------
@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")

    contents = await file.read()
    result = {"file_name": file.filename, "pages": []}

    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""

                # Extract images
                images_b64 = []
                for img in page.images:
                    try:
                        bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                        extracted_img = page.crop(bbox).to_image(resolution=300).original
                        buf = io.BytesIO()
                        extracted_img.save(buf, format="PNG")
                        images_b64.append(base64.b64encode(buf.getvalue()).decode())
                    except:
                        continue

                result["pages"].append({
                    "page_number": i,
                    "text": text,
                    "images_base64": images_b64
                })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {e}")

    return JSONResponse(content=result)


# ----------------------------------------------------------
# 2️⃣ OCR EXTRACTION (Bangla + English)
# ----------------------------------------------------------
@app.post("/extract_ocr")
async def extract_pdf_ocr(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")

    contents = await file.read()

    try:
        pages = convert_from_bytes(contents, dpi=300)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to image conversion failed: {e}")

    result = {"file_name": file.filename, "pages": []}

    for page_number, img in enumerate(pages, start=1):

        # Convert PIL → NumPy
        img_np = np.array(img)

        # Grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        # Upscale for better OCR
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        # Contrast boost
        gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=25)

        # Thresholding to thicken text
        processed = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 8
        )

        processed_pil = Image.fromarray(processed)

        # Run OCR
        try:
            ocr_results = reader.readtext(processed_pil)
            text = "\n".join([res[1] for res in ocr_results])
        except Exception as e:
            text = ""
            print(f"OCR error: {e}")

        # Convert back to Base64
        buf = io.BytesIO()
        processed_pil.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        result["pages"].append({
            "page_number": page_number,
            "ocr_text": text,
            "page_image_base64": img_b64
        })

    return JSONResponse(content=result)
