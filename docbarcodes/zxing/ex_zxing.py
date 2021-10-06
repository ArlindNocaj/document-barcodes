import os
from collections import namedtuple
from pathlib import Path

import cv2
import zxing

RegionBarcode = namedtuple('RegionBarcode', 'page num barcode file region')
DocBarcode = namedtuple('DocBarcode', ['page', 'num_candidate', 'raw', 'format', 'points', 'resultMetadata'])


def extract_barcode(file_name, page_regions, tmp_dir="/tmp"):
    p = Path(file_name)
    files = []
    doc_barcodes = []

    for page, regions in enumerate(page_regions):
        for num, region in enumerate(regions):
            # logger.info(f"page {page}, {regwion.rect}")
            num_resize = 1
            image_resized = region.image
            for num_resize, (image_resized, scale) in enumerate(resize_images(region.image)):
                barcode_file = os.path.join(tmp_dir, p.stem, f"barcode_{page}_{num}_{scale}.png")
                os.makedirs(Path(barcode_file).parent.absolute(), exist_ok=True)
                cv2.imwrite(barcode_file, image_resized)
                # scale points to [0,1] scale
                d_barcode = RegionBarcode(page, num, None, Path(barcode_file).name, region)
                files.append(barcode_file)
                doc_barcodes.append(d_barcode)
    reader = zxing.BarCodeReader()
    possible_formats = ["PDF_417", "CODE_128", "QR_CODE", "AZTEC"]
    if len(files) == 0:
        return []
    barcodes = reader.decode(files, pure_barcode=False, possible_formats=possible_formats, try_harder=True)

    # we assume that we have duplicated the image two times
    # get the first barcode for each image bucket
    step = 2
    doc_final = []
    # take only the first valid barcode for each batch, since we have the same multiple times to increase successrate
    for i in range(0, len(barcodes), step):
        for sub_index in range(i, i + step):
            barcode_raw = barcodes[sub_index]
            if barcode_raw is not None:
                old = doc_barcodes[i]
                points = list(map(tuple, old.region.box_percent.tolist()))
                barcode_final = DocBarcode(old.page, old.num, barcode_raw.raw, barcode_raw.format, points, {})
                doc_final.append(barcode_final)
                break

    return doc_final


def resize_images(image, scale_range=range(20, 300, 50)):
    yield image, 100
    scale_to_3k = 3000 / image.shape[1] * 100
    r = [scale_to_3k] + list(scale_range)
    r = [scale_to_3k]

    for scale_percent in r:
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        yield resized, scale_percent
