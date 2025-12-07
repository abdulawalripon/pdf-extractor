# PDF Extractor API (FastAPI)

This is a simple API that extracts data from PDF files.

It returns:

- Extracted text from each page
- Full page images (as Base64 PNG)
- Embedded images inside the PDF (as Base64)

This API is useful when you need to convert PDF documents into JSON format for use in your website or apps.

---

## 🚀 Features
- FastAPI backend
- Extracts text using pdfplumber
- Converts PDF pages into images (Base64)
- Extracts embedded PDF images
- Ready for deployment on Railway.app

---

## 🛠 Requirements

Install Python packages:
pip install -r requirements.txt

yaml
Copy code

---

## ▶ Run Locally

Start the API locally:
uvicorn main:app --reload

sql
Copy code

Open the API docs:
http://127.0.0.1:8000/docs

yaml
Copy code

---

## 📤 Deploy to Railway.app

1. Upload this project to GitHub  
2. Go to https://railway.app  
3. Create a new project → Deploy from GitHub  
4. Set Start Command:
uvicorn main:app --host 0.0.0.0 --port $PORT

yaml
Copy code

Your API will be live online!

---

## 📁 Project Structure

pdf-extractor/
│── main.py
│── requirements.txt
│── README.md
│── .gitignore

yaml
Copy code

---

## 📞 Support

If you want help adding OCR, scanning PDFs, or building a frontend website,
just ask anytime.
