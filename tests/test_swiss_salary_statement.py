import sys
from docbarcodes.extract import process_document, process_document_old
from conftest import round_floats
import yaml

def named_tuple(self, data):
    if hasattr(data, '_asdict'):
        return self.represent_dict(data._asdict())
    return self.represent_list(data)

yaml.SafeDumper.yaml_multi_representers[tuple] = named_tuple

def test_swiss_salary_statement(data_regression):
    file = "data/salary_swissdec/COMPLEXCompanyMixedSalaries.pdf"

    if sys.platform.startswith("win"):
        barcodes_raw, barcodes_combined = process_document(file, 2)
        raw_baseline = file + ".barcodes_raw_jpype.yml"
        combined_baseline = file + ".barcodes_combined_jpype.yml"
    else:
        barcodes_raw, barcodes_combined = process_document_old(file, 2)
        raw_baseline = file + ".barcodes_raw.yml"
        combined_baseline = file + ".barcodes_combined.yml"

    data_regression.check(round_floats(barcodes_raw), fullpath=raw_baseline)
    data_regression.check(round_floats(barcodes_combined), fullpath=combined_baseline)
