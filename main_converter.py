from csv_converter import CsvConverter, ConverterInterface
from excel_converter import ExcelConverter
from models.convert_param_model import ConvertParameters
from typing import Any
import pandas

class Converter(ConverterInterface):
    __converter_csv = CsvConverter()
    __converter_excel = ExcelConverter()

    def convert_to_json(self, file_path: str) -> str:
        split_arr = file_path.split(sep=".")
        extension = split_arr[len(split_arr)-1]
        if extension == "xlsx":
            return self.__converter_excel.convert_to_json(file_path=file_path)

        elif extension == "csv" or extension == "tsv":
            return self.__converter_csv.convert_to_json(file_path=file_path)

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters) -> str:
        split_arr = file_path.split(sep=".")
        extension = split_arr[len(split_arr)-1]
        if extension == "xlsx":
            return self.__converter_excel.convert_to_json_with_parameters(file_path=file_path, parameters=parameters)

        elif extension == "csv" or extension == "tsv":
            return self.__converter_csv.convert_to_json_with_parameters(file_path=file_path, parameters=parameters)