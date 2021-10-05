import json

from docbarcodes.zxing.extract import process_document


def test_json_serializable():
    file = "data/salary_swissdec/SalarySinglePage.pdf"

    barcodes_raw, barcodes_combined = process_document(file, max_pages=None, use_jpype=True)
    raw_dict = [b._asdict() for b in barcodes_raw]
    combined_dict = [b._asdict() for b in barcodes_combined]

    response = {"BarcodesRaw": raw_dict, "BarcodesCombined": combined_dict}

    res = json.dumps(response)
    assert res