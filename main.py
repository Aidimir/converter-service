from excel_converter import ExcelConverter
from models.convert_param_model import ConvertParameters
import main_converter
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
converter = main_converter.ConverterInterface
if __name__ == '__main__':
    params_dict = {"fer": str}
    params = ConvertParameters(params_dict)
    inp = "Книга1.xlsx"
    converter = main_converter.Converter()
    print(converter.convert_to_json(file_path=inp))