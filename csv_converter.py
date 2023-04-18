from models.convert_param_model import ConvertParameters
import pandas
from typing import Any

class ConverterInterface:
    def convert_to_json(self, file_path: str) -> str:
        pass

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters) -> str:
        pass

    def get_headers(self, file_path: str) -> dict[str, Any]:
        split_arr = file_path.split(sep=".")
        extension = split_arr[len(split_arr)-1]
        headers = dict[str, Any]
        if extension == "xlsx":
            headers = pandas.read_excel(file_path).to_dict().keys()
        elif extension == "csv" or extension == "tsv":
            headers = pandas.read_csv(file_path).to_dict().keys()

        return headers

class CsvConverter(ConverterInterface):
    def convert_to_json(self, file_path: str) -> str:
        csv_data_df = pandas.read_csv(file_path)
        json_str = csv_data_df.to_json(indent=4)
        return json_str

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters) -> str:
        csv_data_df = pandas.read_csv(file_path)
        csv_dict = csv_data_df.to_dict()