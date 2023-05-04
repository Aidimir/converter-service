import io
import uuid

from excel_converter import ExcelConverter
from models.convert_param_model import ConvertParameters
import main_converter
from json import loads, dumps
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, Response
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
app = FastAPI()

@app.get("/")
async def root():
    print("welcome")

@app.post("/upload")
async def upload(uploaded_file: UploadFile):
    id = uuid.uuid4()
    suffix = Path(uploaded_file.filename).suffix
    file_name = str(id) + suffix
    with open(f"storage/{file_name}", "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    return {"file_name": file_name}
@app.get("/headers/{file_name}")
async def get_headers(file_name: str):
    file_path = f"storage/{file_name}"
    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="No such file or directory")
    converter = main_converter.Converter()
    return converter.get_headers(file_path=file_path)

@app.get("/convert/{file_name}")
async def convert_to_json(file_name: str):
    file_path = f"storage/{file_name}"
    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="No such file or directory")
    converter = main_converter.Converter()
    str_json = converter.convert_to_json(file_path)
    return str_json
