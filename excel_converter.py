from csv_converter import ConverterInterface
from models.convert_param_model import ConvertParameters
import pandas
from json import dumps, dump, loads
from typing import Dict

class ExcelConverter(ConverterInterface):
    def convert_to_json(self, file_path: str):
        excel_file = pandas.ExcelFile(file_path)
        pages = excel_file.sheet_names
        pages_dict: Dict[str, str] = {}
        for i in pages:
            excel_data_df = pandas.read_excel(excel_file, i)
            excel_data_df = excel_data_df.dropna(how="all")
            json_string = loads(excel_data_df.to_json(indent=4, orient="records"))
            pages_dict[i] = json_string

        return pages_dict

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters):
        excel_data_df = pandas.read_excel(file_path)

        excel_dict = excel_data_df.to_dict()
        for key in parameters.params_dict.keys():
            for i in range(0, len(list(excel_dict[key].values()))):
                val = parameters.params_dict[key](list(excel_dict[key].values())[i])
                excel_dict[key][i] = val
        dataframe = pandas.DataFrame.from_dict(excel_dict)
        json_string = dataframe.to_json(indent=4, orient="records")
        return json_string
