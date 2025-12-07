import io
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# PDF libraries
import pdfplumber
from pdf2image import convert_from_bytes

# OCR
import easyocr

# Image processing
from PIL import Image

# Initialize EasyOCR (Bangla + English) once
reader = easyocr.Reader(['bn', 'en'], gpu=False)

app = FastAPI(title="PDF Extractor API (Normal + EasyOCR)")


# ----------------------------------------------------------
# 1️⃣ NORMAL EXTRACTION (pdfplumber)
# ----------------------------------------------------------
@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    """ Extract text & images using pdfplumber (fast, but cannot fix broken Bangla). """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")

    contents = await file.read()
    result = {"file_name": file.filename, "pages": []}

    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()

                # Extract images
                images_b64 = []
                for img in page.images:
                    try:
                        bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                        extracted_img = page.crop(bbox).to_image(resolution=300).original

                        buffer = io.BytesIO()
                        extracted_img.save(buffer, format="PNG")
                        images_b64.append(base64.b64encode(buffer.getvalue()).decode())
                    except:
                        continue

                result["pages"].append({
                    "page_number": page_number,
                    "text": text if text else "",
                    "images_base64": images_b64
                })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

    return JSONResponse(content=result)


# ----------------------------------------------------------
# 2️⃣ OCR EXTRACTION (EasyOCR)
# ----------------------------------------------------------
@app.post("/extract_ocr")
async def extract_pdf_ocr(file: UploadFile = File(...)):
    """ Extract Bangla + English text using EasyOCR. """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")

    contents = await file.read()

    # Convert PDF to image pages
    try:
        pages = convert_from_
