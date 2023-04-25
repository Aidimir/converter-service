from models.convert_param_model import ConvertParameters
from pathlib import Path
from json import dumps
import pandas
from typing import Any, Iterable, List, Dict

class ConverterInterface:
    def convert_to_json(self, file_path: str) -> str:
        pass

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters) -> str:
        pass

    def get_headers(self, file_path: str) -> str:
        headers: Dict[str, str] = {}
        as_dict = dict[str, Iterable]
        extension = Path(file_path).suffix

        if extension == ".xlsx":
            as_dict = pandas.read_excel(file_path).to_dict()
        elif extension == ".csv" or extension == ".tsv":
            as_dict = pandas.read_csv(file_path).to_dict().keys()

        keys = as_dict.keys()

        for key in keys:
            headers[key] = type(as_dict[key][0]).__name__

        return dumps(headers, indent=4)
class CsvConverter(ConverterInterface):
    def convert_to_json(self, file_path: str) -> str:
        csv_data_df = pandas.read_csv(file_path)
        json_str = csv_data_df.to_json(indent=4)
        return json_str

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters) -> str:
        csv_data_df = pandas.read_csv(file_path)
        csv_dict = csv_data_df.to_dict()
        for key in parameters.params_dict.keys():
            for i in range(0, len(list(csv_dict[key].values()))):
                val = parameters.params_dict[key](list(csv_dict[key].values())[i])
                csv_dict[key][i] = val

        return dumps(csv_dict, indent=4)