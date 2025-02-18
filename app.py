from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os

app = FastAPI()

UPLOAD_FOLDER = "/app/static/images"  # Carpeta dentro del servidor en Render
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crear la carpeta si no existe

@app.post("/upload_images")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    Permite a OpenAI subir imágenes al servidor y guardarlas para el procesamiento.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se han recibido archivos.")

    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file_path)
    
    return {"message": "Imágenes subidas correctamente", "files": saved_files}
