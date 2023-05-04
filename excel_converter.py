from csv_converter import ConverterInterface
from models.convert_param_model import ConvertParameters
import pandas
from json import dumps, loads

class ExcelConverter(ConverterInterface):
    def convert_to_json(self, file_path: str):
        excel_data_df = pandas.read_excel(file_path)

        json_string = excel_data_df.to_json(indent=4)

        return json_string

    def convert_to_json_with_parameters(self, file_path: str, parameters: ConvertParameters):
        excel_data_df = pandas.read_excel(file_path)

        excel_dict = excel_data_df.to_dict()
        for key in parameters.params_dict.keys():
            for i in range(0, len(list(excel_dict[key].values()))):
                val = parameters.params_dict[key](list(excel_dict[key].values())[i])
                excel_dict[key][i] = val

        return dumps(excel_dict, indent=4)
