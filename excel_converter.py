from csv_converter import ConverterInterface
from models.convert_param_model import ConvertParameters
import pandas
from json import dumps, dump, loads
from typing import Dict, Union, Any

class ExcelConverter(ConverterInterface):
    def convert_to_json(self, file_path: str, null_replacing: Union[Any, None] = None):
        excel_file = pandas.ExcelFile(file_path)
        pages = excel_file.sheet_names
        pages_dict: Dict[str, str] = {}
        for i in pages:
            excel_data_df = pandas.read_excel(excel_file, i)
            if null_replacing != None:
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
            if null_replacing != None:
                page_df.fillna(null_replacing, inplace=True)
            if page in parameters.params_dict:
                excel_dict = page_df.to_dict()
                for param_row_name in parameters.params_dict[page]:
                    for j in range(len(excel_dict[param_row_name])):
                        val = parameters.params_dict[page][param_row_name](excel_dict[param_row_name][j])
                        excel_dict[param_row_name][j] = val
                pages_dict[page] = loads(pandas.DataFrame.from_dict(excel_dict).to_json(indent=4, orient="records"))
            else:
                json_string = loads(pandas.read_excel(excel_file, page).to_json(indent=4, orient="records"))
                pages_dict[page] = json_string
        json_string = dumps(pages_dict)
        return loads(json_string)
