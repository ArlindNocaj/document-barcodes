from docbarcodes.extract import process_document
import yaml

def named_tuple(self, data):
    if hasattr(data, '_asdict'):
        return self.represent_dict(data._asdict())
    return self.represent_list(data)

yaml.SafeDumper.yaml_multi_representers[tuple] = named_tuple

def test_swiss_salary_statement(data_regression):
    file = "data/salary_swissdec/COMPLEXCompanyMixedSalaries.pdf"

    barcodes_raw, barcodes_combined = process_document(file,2)
    data_regression.check(barcodes_raw, fullpath=file+".barcodes_raw_jpype.yml")
    data_regression.check(barcodes_combined, fullpath=file + ".barcodes_combined_jpype.yml")