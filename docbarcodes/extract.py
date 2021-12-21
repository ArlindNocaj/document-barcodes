import io
import pathlib
import zipfile
import zlib
from collections import namedtuple
from typing import Union

from loguru import logger
import itertools
from docbarcodes.zxing.ex_zxing import extract_barcode
from docbarcodes.convertpdf import convert_pdf_to_images
from docbarcodes.detect import detect_regions_multipage
from docbarcodes.zxingjpype.extract import extract_barcode_jpype
import cv2
import tempfile

DocBarcodeCombined = namedtuple('DocBarcodeCombined', ['content', 'format', 'sources'])


def log_barcodes(docbarcodes):
    for x in docbarcodes:
        logger.debug(x)


def combine_barcodes(docbarcodes):
    results = []

    if len(docbarcodes) == 0:
        return results
    pdf_417 = [(ind, doc_bar.raw) for ind, doc_bar in enumerate(docbarcodes) if doc_bar.format == "PDF_417"]

    results_a = _decompress_content(pdf_417)
    results_b = _decompress_zip(pdf_417)
    merged = results_a + results_b
    for (content, indices) in merged:
        barcode_combined = DocBarcodeCombined(content, "PDF_417", indices)
        results.append(barcode_combined)
    return results


def _decompress_zip(index_barcodes):
    pdf_417 = [barcode for ind, barcode in index_barcodes]
    indices = [ind for ind, barcode in index_barcodes]
    header = bytearray.fromhex("504b0304")
    pk_arr = [b.encode("ISO-8859-1") for b in pdf_417]
    # split header to get ordering and prefix
    pk_salary = [(index, arr[:4], int.from_bytes(arr[10:12], "little"), int.from_bytes(arr[12:14], "little"), arr) for
                 index, arr in enumerate(pk_arr)]
    bargroups = itertools.groupby(pk_salary, lambda x: x[1])

    data = []
    for prefix, group in bargroups:
        l_barcodes = list(group)
        group_indices = [indices[tup[0]] for tup in l_barcodes]
        l_barcodes_sort = sorted(l_barcodes, key=lambda x: x[2])
        arr_bytes = [arr for (index, prefix, num, total, arr) in l_barcodes_sort]
        arr_clean = [a[a.find(header):] for a in arr_bytes]
        # for a in arr_clean: logger.info(a.hex())
        all_bytes = b''.join(arr_clean)

        try:
            zf = zipfile.ZipFile(io.BytesIO(all_bytes), "r")
            content = zf.read(zf.infolist()[0])
            content = content.decode("ISO-8859-1")
            data.append((content, group_indices))
        except (IOError, zlib.error, zipfile.BadZipFile):
            # logger.warning(error)
            # for e in arr_clean:
            #     logger.warning(e)
            pass
    return data


def _decompress_content(index_barcodes):
    pdf_417 = [barcode for ind, barcode in index_barcodes]
    indices = [ind for ind, barcode in index_barcodes]
    all_bytes = "".join(pdf_417).encode("ISO-8859-1")
    if len(pdf_417) == 0:
        return []
    # logger.info(f"Length of combined PDF_417 barcodes: {len(all_bytes)}")
    try:
        # try deflate decompress
        content = zlib.decompress(all_bytes).decode('utf8')
    except (IOError, zlib.error):
        # logger.debug(f"deflate decompress failed for: {pdf_417}")
        # for row in pdf_417:
        #     logger.debug(f"Bytes Hex: {row.encode('ISO-8859-1').hex()}")
        return []
        # raise RuntimeError("deflate decompress did not work.")
    return [(content, indices)]


def process_document(file_name, max_pages: Union[None, int] = 2, debug=False,
                     use_jpype=True, try_harder=True, possible_formats=["PDF_417", "CODE_128", "QR_CODE", "AZTEC"]):
    if not use_jpype:
        return process_document_old(file_name, max_pages, debug)

    images = _get_images(file_name, max_pages)
    page_regions = detect_regions_multipage(images)
    logger.info(f"detected regions: {len(page_regions)}")

    barcodes_raw = extract_barcode_jpype(file_name, page_regions,
                                         try_harder=try_harder, possible_formats=possible_formats)
    logger.info(f"extracted raw barcodes: {len(barcodes_raw)}")

    if debug:
        log_barcodes(barcodes_raw)

    barcode_combined = combine_barcodes(barcodes_raw)
    logger.info(f"extracted combined barcodes: {len(barcode_combined)}")

    if debug:
        log_barcodes(barcode_combined)
    return barcodes_raw, barcode_combined


def _get_images(file_name, max_pages):
    suffix = pathlib.Path(file_name).suffix.lower()
    if suffix == ".pdf":
        images = convert_pdf_to_images(file_name, last_page=max_pages)
        return images

    image = cv2.imread(str(file_name))
    return [image]


def process_document_old(file_name, max_pages=2, debug=False):
    """
    Extracts barcodes using python-zxing wrapper, for which the files are being saved
    and passed through as URIs when calling zxing CommandLineRunner.
    This approach should be avoided, as it does not provide the metadata e.g. for PDF417.
    :param file_name:
    :param max_pages:
    :param debug:
    :return:
    """
    images = _get_images(file_name, max_pages)
    page_regions = detect_regions_multipage(images)
    logger.info(f"detected regions: {len(page_regions)}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        barcodes_raw = extract_barcode(file_name, page_regions, tmp_dir)
        logger.info(f"extracted raw barcodes: {len(barcodes_raw)}")

    if debug:
        log_barcodes(barcodes_raw)

    barcode_combined = combine_barcodes(barcodes_raw)
    logger.info(f"extracted combined barcodes: {len(barcode_combined)}")

    if debug:
        log_barcodes(barcode_combined)
    return barcodes_raw, barcode_combined


if __name__ == '__main__':
    import timeit

    start = timeit.default_timer()
    #codes_raw, codes_combined = process_document("data/ZH Tax Sample - Formular 1.ptax20.pdf", None)
    barcodes_raw, barcodes_combined = process_document("data/ZH Tax Sample - Formular 1.ptax20.pdf", None)
    # log_barcodes(barcodes_raw)
    # log_barcodes(barcodes_combined)

    # process_document("data/Covid Zertifikat Arlind Nocaj.salary_swissdec")
    # process_document("data/2021_LA_756.1234.5678.97_Musterfrau_Tamara_01_12.salary_swissdec")
    # process_document("data/2021_LA_756.1234.5678.97_Musterfrau_Tamara_01_12-B.salary_swissdec")
    #barcodes_raw, barcodes_combined = process_document("data/salary_swissdec/COMPLEXCompanyMixedSalaries.pdf",1)
    # barcodes_raw, barcodes_combined = process_document("data/drivers-license-Sample.FL.DL.PDF", 2)
    #barcodes_raw, barcodes_combined = process_document("/Users/arlnocaj/projects/document-barcodes/CNI-verso.jpeg", 2)
    #barcodes_raw, barcodes_combined = process_document("test.png")


    log_barcodes(barcodes_raw)
    log_barcodes(barcodes_combined)
    stop = timeit.default_timer()
    print('Time: ', stop - start)
