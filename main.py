from typing import Union
import uuid
import main_converter
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
uploads_description = """
Uploads file on the server. The **extension validation** logic is also here.\n
supported extensions: .xlsx, .csv, .tsv.
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

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
