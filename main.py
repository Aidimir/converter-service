from typing import Union, Dict, Any
from datetime import datetime
import uuid
import main_converter
from pathlib import Path
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import arrow
import os
import threading
from models.convert_param_model import ConvertParameters


# class HeaderResponseModel(BaseModel):
#     sheet_name: dict[str,str]
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "sheet1": {"price": "int", "title": "str"}
#             }
#         }


# class UploadResponseModel(BaseModel):
#     file_name: str
#     file_size: int
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "file_name": "ew2ewsr31rdsd.xlsl",
#                 "file_size": "80000",
#             }
#         }
#
#
# class ConvertResponseModel(BaseModel):
#     sheet_name: dict[str,str]
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "sheet1": {"price": "10", "title": "apple", "is_cheap": "true" },
#                 "sheet2": {"price": "0", "title": "ban", "is_cheap": "false" },
#             }
#         }

def clear_storage():
    threading.Timer(interval=3600.0, function=clear_storage).start()
    files_path = "storage/"

    critical_time = arrow.now().shift(hours=-1)

    for item in Path(files_path).glob('*'):
        if item.is_file():
            itemTime = arrow.get(item.stat().st_mtime)
            if itemTime < critical_time:
                os.remove(item.absolute())


uploads_description = """
Uploads file on the server. The **extension validation** logic is also here.\n
Supported extensions: .xlsx, .csv, .tsv.\n
"""

get_headers_description = "Fetches columns data types for each page of document."

convert_description = "Converts files to json. If request contain convert parameters will change columns data-type."

tags_metadata = [
    {
        "name": "upload",
        "description": uploads_description,
    },
    {
        "name": "headers",
        "description": get_headers_description,
    },
    {
        "name": "convert",
        "description": convert_description,
    },
]

description = """
ConverterService API made to convert xlsx, csv and tsv files to json. 🚀

## Converting

You will be able to:

* **Simple json convert**.
* **Convert to json with type parameters**.
"""


app = FastAPI(title="ConverterService",
              description=description,
              version="0.0.1",
              openapi_tags=tags_metadata,
              docs_url=None,
              redoc_url=None,
              )
app.mount("/", StaticFiles(directory="static", html=True), name="static")


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:4200",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clear_storage()
@app.get("/")
async def root():
    print("welcome")

@app.post("/upload", tags=["upload"])
async def upload(uploaded_file: UploadFile):
    id = uuid.uuid4()
    suffix = Path(uploaded_file.filename).suffix
    file_name = str(id) + suffix
    file_size = uploaded_file.size
    if file_size/(2**30) >= 1:
        raise HTTPException(status_code=400, detail="File size is too big")
    if suffix == ".csv" or suffix == ".tsv" or suffix == ".xlsx":
        with open(f"storage/{file_name}", "wb+") as file_object:
            file_object.write(uploaded_file.file.read())
        return {"file_name": file_name, "file_size": file_size}
    else:
        raise HTTPException(status_code=400, detail="Unacceptable data format")
@app.get("/headers/{file_name}", tags=["headers"])
async def get_headers(file_name: str):
    file_path = f"storage/{file_name}"
    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="No such file or directory")
    converter = main_converter.Converter()
    return converter.get_headers(file_path=file_path)


@app.get("/convert/{file_name}", tags=["convert"])
async def convert_to_json(file_name: str, parameters: Union[Dict, None] = None):
    file_path = f"storage/{file_name}"
    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="No such file or directory")
    converter = main_converter.Converter()
    if parameters == None:
        str_json = converter.convert_to_json(file_path)
        return str_json
    else:
        dict_with_classes: Dict[str, Any] = {}
        for key in parameters:
            if parameters[key] == "str":
                dict_with_classes[key] = str
            elif parameters[key] == "float":
                dict_with_classes[key] = float
            elif parameters[key] == "int":
                dict_with_classes[key] = int
            elif parameters[key] == "Timestamp":
                dict_with_classes[key] = datetime
            elif parameters[key] == "bool":
                dict_with_classes[key] = bool
        params = ConvertParameters(params_dict=dict_with_classes)
        str_json = converter.convert_to_json_with_parameters(file_path=file_path, parameters=params)
        return str_json

