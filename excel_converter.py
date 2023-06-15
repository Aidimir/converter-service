from csv_converter import ConverterInterface
from models.convert_param_model import ConvertParameters
import pandas
from json import dumps, loads
from typing import Dict, Union, Any

class ExcelConverter(ConverterInterface):
    def convert_to_json(self, file_path: str, null_replacing: Union[Any, None] = None):
        excel_file = pandas.ExcelFile(file_path)
        pages = excel_file.sheet_names
        pages_dict: Dict[str, str] = {}
        for i in pages:
            excel_data_df = pandas.read_excel(excel_file, i)
            if null_replacing is not None:
                excel_data_df.fillna(null_replacing, inplace=True)
            else:
                excel_data_df = excel_data_df.dropna(how="all")
            json_string = loads(excel_data_df.to_json(indent=4, orient="records"))
            pages_dict[i] = json_string

        return pages_dict

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters, null_replacing: Union[Any, None] = None):
        excel_file = pandas.ExcelFile(file_path)
        pages = excel_file.sheet_names
        pages_dict: Dict[str, str] = {}
        for page in pages:
            page_df = pandas.read_excel(excel_file, page)
            if page in parameters.params_dict:
                page_df = pandas.read_excel(excel_file, page, converters=parameters.params_dict[page])
                if null_replacing is not None:
                    page_df.fillna(null_replacing, inplace=True)
                pages_dict[page] = loads(page_df.to_json(indent=4, orient="records"))
            else:
                if null_replacing is not None:
                    page_df.fillna(null_replacing, inplace=True)
                json_string = loads(page_df.to_json(indent=4, orient="records"))
                pages_dict[page] = json_string
        json_string = dumps(pages_dict)
        return loads(json_string)