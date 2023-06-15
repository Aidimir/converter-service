from typing import Union, Dict, Any, Annotated
from datetime import datetime
import uuid

import pandas
from json import loads, dumps
import main_converter
from pathlib import Path
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import arrow
import os
import threading
from io import StringIO
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
              # docs_url=None,
              redoc_url=None,
              )


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


@app.post("/upload", tags=["upload"])
async def upload(uploaded_file: UploadFile):
    id = uuid.uuid4()
    suffix = Path(uploaded_file.filename).suffix
    file_size = uploaded_file.size
    file_name = str(id) + suffix
    if file_size/(2**30) >= 1:
        raise HTTPException(status_code=400, detail="File size is too big")
    if suffix == ".csv" or suffix == ".tsv" or suffix == ".xlsx":
        with open(f"storage/{file_name}", "wb+") as file_object:
            file_object.write(uploaded_file.file.read())
        return {"file_name": file_name, "file_size": file_size}
    else:
        raise HTTPException(status_code=400, detail="Unacceptable data format")

@app.post("/upload/text")
async def upload_text(body: str = Body(..., media_type="text/plain")):
    id = uuid.uuid4()
    file_size = len(body.encode('utf-8'))
    csv_df: pandas.DataFrame
    suffix = ".csv"
    file_name = str(id) + suffix
    separator = "\t"
    for i in body.splitlines():
        if i.split(sep="\t") != 0 and i.split(sep="\t") <= i.split(sep=","):
            separator = "\t"
            break
        elif i.split(sep=",") != 0 and i.split(sep=",") < i.split(sep="\t"):
            separator = ","
            break
    csv_df = pandas.read_csv(StringIO(body), index_col=0, skipinitialspace=True, sep=separator)
    csv_df.to_csv(f"storage/{file_name}")
    return {"file_name": file_name, "file_size": file_size}

@app.get("/headers/{file_name}", tags=["headers"])
async def get_headers(file_name: str):
    file_path = f"storage/{file_name}"
    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="No such file or directory")
    converter = main_converter.Converter()
    return converter.get_headers(file_path=file_path)


@app.get("/convert/{file_name}", tags=["convert"])
async def convert_to_json(file_name: str,
                          parameters: Union[str, None] = None,
                          null_replacing: Union[Any, None] = None):
    file_path = f"storage/{file_name}"
    if not Path(file_path).exists():
        raise HTTPException(status_code=400, detail="No such file or directory")
    converter = main_converter.Converter()
    if parameters is None:
        str_json = converter.convert_to_json(file_path, null_replacing=null_replacing)
        return str_json
    else:
        dict_parameters = loads(parameters)
        dict_with_classes: Dict[str, Dict[str, Any]] = {}
        for page in dict_parameters:
            dict_with_classes[page] = {}
            for key in dict_parameters[page]:
                if dict_parameters[page][key] == "str":
                    dict_with_classes[page][key] = converter_str
                elif dict_parameters[page][key] == "float":
                    dict_with_classes[page][key] = converter_float
                elif dict_parameters[page][key] == "int":
                    dict_with_classes[page][key] = converter_int
                elif dict_parameters[page][key] == "Timestamp":
                    dict_with_classes[page][key] = converter_timestamp
                elif dict_parameters[page][key] == "bool":
                    dict_with_classes[page][key] = converter_bool
                elif dict_parameters[page][key] == "array":
                    dict_with_classes[page][key] = converter_array
                else:
                    dict_with_classes[page][key] = None
        params = ConvertParameters(params_dict=dict_with_classes)
        str_json = converter.convert_to_json_with_parameters(file_path=file_path, parameters=params, null_replacing=null_replacing)
        return str_json


app.mount("/", StaticFiles(directory="static", html=True), name="static")

def converter_str(col):
    return str(col)

def converter_float(col):
    try:
        res = float(col)
        return res
    except:
        return None

def converter_int(col):
    try:
        res = int(col)
        return res
    except:
        return None

def converter_timestamp(col):
    try:
        res = datetime(col)
        return res
    except:
        return None

def converter_bool(col):
    try:
        if col is None:
            return False
        elif col is str:
            if col == "0":
                return False
            elif col == "1":
                return True
            elif str(col).lower() == "yes":
                return True
            elif str(col).lower() == "no":
                return False
            else:
                return False
    except:
        return None

def converter_array(col) -> Union[tuple, None]:
    try:
        if col is None:
            return tuple()
        elif type(col) is str:
            if str(col.split(",")[0]).isnumeric():
                dict_res = []
                for i in range(len(str(col).split(sep=","))):
                    dict_res.append(float(str(col).split(sep=",")[i]))
                print(dict_res)
                return tuple(dict_res)
            else:
                dict_res = []
                for i in range(len(str(col).split(sep=","))):
                    dict_res.append(str(col).split(sep=",")[i])
                print(dict_res)
                return tuple(dict_res)
        else:
            print([col])
            return tuple([col])
    except:
        return None
