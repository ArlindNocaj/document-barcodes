import os
from collections import namedtuple
from pathlib import Path

import cv2
import numpy
import numpy as np
import zxing
from loguru import logger

from docbarcodes.zxingjpype.zxingreader import decodeImages

RegionBarcode = namedtuple('RegionBarcode', 'page num barcode file region')
DocBarcode = namedtuple('DocBarcode', ['page', 'num_candidate', 'raw', 'format', 'points', 'resultMetadata'])


def extract_barcode_jpype(file_name, page_regions, try_harder=True, possible_formats=None):
    doc_barcodes = []

    possible_formats = ["PDF_417", "CODE_128", "QR_CODE", "AZTEC"]
    # possible_formats = None
    for page, regions in enumerate(page_regions):
        for num, region in enumerate(regions):
            results = []
            barcodes = []
            for num_resize, (image_resized, scale) in enumerate(resize_images(region.image)):
                results = decodeImages([image_resized], try_harder=try_harder, possible_formats=possible_formats)
                barcodes = results[0]
                if len(barcodes) > 0:
                    break

            if len(barcodes) > 0:
                # conv = []
                points = list(map(tuple, region.box_percent.tolist()))
                for b in barcodes:
                    resultMetadata = b.resultMetadata
                    if "PDF417_EXTRA_METADATA" in resultMetadata:
                        resultMetadata["PDF417_EXTRA_METADATA"] = resultMetadata["PDF417_EXTRA_METADATA"].__dict__
                    barcode_final = DocBarcode(page, num, b.text, b.format,
                                               points, b.resultMetadata)
                    doc_barcodes.append(barcode_final)
                # doc_barcodes.append(conv)

    return doc_barcodes


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
