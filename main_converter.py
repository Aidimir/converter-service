from csv_converter import CsvConverter, ConverterInterface
from excel_converter import ExcelConverter
from models.convert_param_model import ConvertParameters
from typing import Any, Union
import pandas

class Converter(ConverterInterface):
    __converter_csv = CsvConverter()
    __converter_excel = ExcelConverter()

    def convert_to_json(self, file_path: str, null_replacing: Union[Any, None] = None) -> str:
        split_arr = file_path.split(sep=".")
        extension = split_arr[len(split_arr)-1]
        if extension == "xlsx":
            return self.__converter_excel.convert_to_json(file_path=file_path, null_replacing=null_replacing)

        elif extension == "csv" or extension == "tsv":
            return self.__converter_csv.convert_to_json(file_path=file_path, null_replacing=null_replacing)

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters, null_replacing: Union[Any, None] = None) -> str:
        split_arr = file_path.split(sep=".")
        extension = split_arr[len(split_arr)-1]
        if extension == "xlsx":
            return self.__converter_excel.convert_to_json_with_parameters(file_path=file_path, parameters=parameters, null_replacing=null_replacing)

        elif extension == "csv" or extension == "tsv":
            return self.__converter_csv.convert_to_json_with_parameters(file_path=file_path, parameters=parameters, null_replacing=null_replacing)