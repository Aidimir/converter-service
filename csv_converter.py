from models.convert_param_model import ConvertParameters
from pathlib import Path
from json import dumps, loads
import pandas
from typing import Dict, Union, Any

class ConverterInterface:
    def convert_to_json(self, file_path: str, null_replacing: Union[Any, None] = None) -> str:
        pass

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters, null_replacing: Union[Any, None] = None) -> str:
        pass

    def get_headers(self,
                    file_path: Union[str, None] = None,
                    string_version: Union[str, None] = None) -> str:
        if string_version is not None:
            res = ""
            for i in string_version:
                res += f"\n{i}"
            return res

        extension = Path(file_path).suffix

        if extension == ".xlsx":
            headers: Dict[str, Dict[str, str]] = {}
            excel_file = pandas.ExcelFile(file_path)
            pages = excel_file.sheet_names
            for i in pages:
                headers[i] = {}
                excel_data_df = pandas.read_excel(excel_file, i)
                json_dict = excel_data_df.to_dict()
                for key in json_dict.keys():
                    headers[i][key] = type(json_dict[key][0]).__name__
            return loads(dumps(headers, indent=4))

        elif extension == ".csv" or extension == ".tsv":
            as_dict = pandas.read_csv(file_path, encoding="ISO-8859-1", skipinitialspace=True).to_dict()
            headers: Dict[str, Dict[str, str]] = {}
            headers["csv page"] = {}

            for key in as_dict:
                headers["csv page"][key] = type(as_dict[key][0]).__name__

            return loads(dumps(headers, indent=4))


class CsvConverter(ConverterInterface):
    def convert_to_json(self, file_path: str, null_replacing: Union[Any, None] = None) -> str:
        csv_data_df = pandas.read_csv(file_path, encoding="ISO-8859-1")
        if null_replacing is not None:
            csv_data_df.fillna(null_replacing, inplace=True)
        json_str = csv_data_df.to_json(indent=4, orient="records")
        return loads(json_str)

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters, null_replacing: Union[Any, None] = None) -> str:
        if len(parameters.params_dict.values()) == 1:
            params_dict = list(parameters.params_dict.values())[0]
            csv_data_df = pandas.read_csv(file_path, encoding="ISO-8859-1")
            if null_replacing is not None:
                csv_data_df.fillna(null_replacing, inplace=True)
            csv_dict = csv_data_df
            for key in params_dict:
                for i in range(0, len(csv_dict[key])):
                    val = params_dict[key](csv_dict[key][i])
                    csv_dict[key][i] = val
            dataframe = pandas.DataFrame.from_dict(csv_dict)
            json_string = dataframe.to_json(indent=4, orient="records")
            return loads(json_string)
        else:
            return self.convert_to_json(file_path, null_replacing=null_replacing)
