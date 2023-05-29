from typing import Union
import uuid
import main_converter
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import arrow
import os
import threading


def clear_storage():
    threading.Timer(interval=3600.0, function=clear_storage).start()
    filesPath = "storage/"

    criticalTime = arrow.now().shift(hours=-1)

    for item in Path(filesPath).glob('*'):
        if item.is_file():
            itemTime = arrow.get(item.stat().st_mtime)
            if itemTime < criticalTime:
                os.remove(item.absolute())


uploads_description = """
Uploads file on the server. The **extension validation** logic is also here.\n
Supported extensions: .xlsx, .csv, .tsv.\n
Expected output structure: \n
    {\n
        "file_name": "fee4b29c.xlsx",\n
        "file_size": 1000 (in bytes)\n
    }
"""

get_headers_description = """
Fetches columns data types for each page of document.\n
Expected output structure:\n 
    {\n
        "page_name1": {"column1_name": "int", "column2_name": "str", "column3_name": "bool"},\n
        "page_name2": {"column1_name": "int", "column2_name": "str", "column3_name": "bool"}\n
    }
"""

convert_description = """
Converts files to json. If request contain convert parameters will change columns data-type.\n
Parameters structure:\n 
    {\n
        "page_name1": {"column1_name": "int", "column2_name": "str", "column3_name": "bool"},\n
        "page_name2": {"column1_name": "int", "column2_name": "str", "column3_name": "bool"}\n
    }
"""

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
    openapi_tags=tags_metadata,)

origins = ["*"]

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
async def convert_to_json(file_name: str, parameters: Union[str, None] = None):
    file_path = f"storage/{file_name}"
    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="No such file or directory")
    converter = main_converter.Converter()
    str_json = converter.convert_to_json(file_path)
    return str_json
