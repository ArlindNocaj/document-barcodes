import os
import re
from collections import namedtuple
from pathlib import Path

import cv2
import zxing
from zxing import CLROutputBlock

RegionBarcode = namedtuple('RegionBarcode', 'page num barcode file region')
DocBarcode = namedtuple('DocBarcode', ['page', 'num_candidate', 'raw', 'format', 'points', 'resultMetadata'])


# Monkey-patch zxing.BarCode.parse to handle non-UTF-8 barcode payloads.
# The zxing CLI wrapper redirects Java's stderr into stdout (stderr=STDOUT)
# and calls bytes.decode() on raw barcode data.  On Windows the JVM writes
# stdout in the system code-page (e.g. cp1252), which causes
# UnicodeDecodeError for non-ASCII barcode payloads.
# We try UTF-8 first (correct on Linux/macOS) and fall back to latin-1
# (losslessly decodes any byte 0x00-0xFF) for Windows / non-UTF-8 output.
def _decode_safe(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin-1')


@classmethod
def _safe_parse(cls, zxing_output):
    block = CLROutputBlock.UNKNOWN
    uri = format = type = None
    raw = parsed = b''
    points = []

    for l in zxing_output.splitlines(True):
        if block == CLROutputBlock.UNKNOWN:
            if l.endswith(b': No barcode found\n'):
                return None
            m = re.match(rb"(\S+) \(format:\s*([^,]+),\s*type:\s*([^)]+)\)", l)
            if m:
                uri, format, type = m.group(1).decode(), m.group(2).decode(), m.group(3).decode()
            elif l.startswith(b"Raw result:"):
                block = CLROutputBlock.RAW
        elif block == CLROutputBlock.RAW:
            if l.startswith(b"Parsed result:"):
                block = CLROutputBlock.PARSED
            else:
                raw += l
        elif block == CLROutputBlock.PARSED:
            if re.match(rb"Found\s+\d+\s+result\s+points?", l):
                block = CLROutputBlock.POINTS
            else:
                parsed += l
        elif block == CLROutputBlock.POINTS:
            m = re.match(rb"\s*Point\s*\d+:\s*\(([\d.]+),([\d.]+)\)", l)
            if m:
                points.append((float(m.group(1)), float(m.group(2))))

    raw = _decode_safe(raw[:-1])
    parsed = _decode_safe(parsed[:-1])
    return cls(uri, format, type, raw, parsed, points)


zxing.BarCode.parse = _safe_parse


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
