import easyocr
import os
import io
import json
import base64
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pdfplumber
from PIL import Image

reader = easyocr.Reader(['bn', 'en'])

app = FastAPI(title="PDF -> JSON Extractor")

@app.post("/extract_ocr")
async def extract_pdf_ocr(file: UploadFile = File(...)):
    contents = await file.read()

    # STEP 3-A: Convert PDF → images
    pages = convert_from_bytes(contents, 300)

    result = {"pages": []}

    for i, img in enumerate(pages, start=1):
        
        # STEP 3-C: Use EasyOCR on the image (place code HERE)
        ocr_results = reader.readtext(img)
        text = "\n".join([r[1] for r in ocr_results])

        # STEP 3-D: Convert page image to Base64 (optional)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode()

        # Add to output
        result["pages"].append({
            "page_number": i,
            "ocr_text": text,
            "page_image_base64": img_b64
        })

    return result

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.post("/extract")
async def extract_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large.")

    stream = io.BytesIO(contents)
    result = {"file_name": file.filename, "pages": []}

    try:
        with pdfplumber.open(stream) as pdf:
            for pnum, page in enumerate(pdf.pages, start=1):
                page_entry = {"page_number": pnum}

                # Extract text
                text = page.extract_text()
                page_entry["text"] = text if text else ""

                # Extract full page image as Base64
                img = page.to_image(resolution=150).original
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                page_entry["page_image_base64"] = base64.b64encode(buf.getvalue()).decode()

                # Extract embedded images (if any)
                images_b64 = []
                for img in page.images:
                    try:
                        bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                        cropped = page.crop(bbox).to_image(resolution=300).original
                        cb = io.BytesIO()
                        cropped.save(cb, format="PNG")
                        images_b64.append({
                            "bbox": bbox,
                            "base64": base64.b64encode(cb.getvalue()).decode()
                        })
                    except:
                        pass
                page_entry["embedded_images"] = images_b64

                result["pages"].append(page_entry)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF parsing error: {str(e)}")

    return JSONResponse(content=result)


