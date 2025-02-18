from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from typing import List

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Asegurar que la carpeta existe

# 📌 Función para crear PowerPoint
def create_powerpoint(images, output_pptx):
    prs = Presentation()
    slide_layout = prs.slide_layouts[5]  # Diapositiva en blanco

    for i in range(0, len(images), 4):
        slide = prs.slides.add_slide(slide_layout)
        img_positions = [(Inches(0.5), Inches(0.5)), (Inches(5.5), Inches(0.5)),
                         (Inches(0.5), Inches(4.5)), (Inches(5.5), Inches(4.5))]

        for j, img_path in enumerate(images[i:i+4]):
            left, top = img_positions[j]
            img = Image.open(img_path)
            width, height = img.size
            aspect_ratio = width / height
            img_width = Inches(4) if aspect_ratio > 1 else Inches(3)
            img_height = Inches(3) if aspect_ratio < 1 else Inches(4)
            slide.shapes.add_picture(img_path, left, top, width=img_width, height=img_height)

    prs.save(output_pptx)

# 📌 Función para crear PDF
def create_pdf(images, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    for i in range(0, len(images), 4):
        for j in range(4):
            if i + j < len(images):
                img_path = images[i + j]
                top = height - (j // 2) * 280 - 40
                left = (j % 2) * 300 + 40
                c.drawImage(img_path, left, top, width=250, height=180)
        c.showPage()

    c.save()

# 📌 Endpoint para recibir imágenes y generar archivos
@app.post("/generate_ppt_pdf")
async def generate_ppt_pdf(files: List[UploadFile] = File(...)):
    """
    Recibe archivos de imagen, los guarda en el servidor y genera un PowerPoint y un PDF.
    """
    image_paths = []

    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        image_paths.append(file_path)

    if not image_paths:
        return JSONResponse(status_code=400, content={"error": "No se encontraron imágenes en la carpeta"})

    output_pptx = os.path.join(UPLOAD_FOLDER, "output_presentation.pptx")
    output_pdf = os.path.join(UPLOAD_FOLDER, "output_document.pdf")

    create_powerpoint(image_paths, output_pptx)
    create_pdf(image_paths, output_pdf)

    return JSONResponse(
        content={
            "pptx_file": output_pptx,
            "pdf_file": output_pdf
        },
        status_code=200
    )

@app.get("/")
async def home():
    return {"message": "API para generar PowerPoint y PDF con imágenes funcionando correctamente."}
