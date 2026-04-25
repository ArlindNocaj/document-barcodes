import os
import re
import pathlib
import subprocess as sp
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


def _safe_decode(self, filenames, try_harder=False, possible_formats=None, pure_barcode=False, products_only=False):
    possible_formats = (possible_formats,) if isinstance(possible_formats, str) else possible_formats

    if isinstance(filenames, str):
        one_file = True
        filenames = (filenames,)
    else:
        one_file = False

    file_uris = [pathlib.Path(f).absolute().as_uri() for f in filenames]
    cmd = [
        self.java,
        "-Dfile.encoding=ISO-8859-1",
        "-cp",
        self.classpath,
        self.cls,
        *file_uris,
    ]
    if try_harder:
        cmd.append("--try_harder")
    if pure_barcode:
        cmd.append("--pure_barcode")
    if products_only:
        cmd.append("--products_only")
    if possible_formats:
        for barcode_format in possible_formats:
            cmd += ["--possible_formats", barcode_format]

    try:
        process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=False)
    except FileNotFoundError as error:
        raise zxing.BarCodeReaderException(
            "Java binary specified (%s) does not exist" % self.java,
            self.java,
            error,
        )
    except PermissionError as error:
        raise zxing.BarCodeReaderException(
            "Java binary specified (%s) is not executable" % self.java,
            self.java,
            error,
        )

    stdout, _ = process.communicate()

    if stdout.startswith((
        b"Error: Could not find or load main class com.google.zxing.client.j2se.CommandLineRunner",
        b'Exception in thread "main" java.lang.NoClassDefFoundError:',
    )):
        raise zxing.BarCodeReaderException("Java JARs not found in classpath (%s)" % self.classpath, self.classpath)
    elif stdout.startswith((
        b'''Exception in thread "main" javax.imageio.IIOException: Can't get input stream from URL!''',
        b'''Exception in thread "main" java.util.concurrent.ExecutionException: javax.imageio.IIOException: Can't get input stream from URL!''',
    )):
        raise zxing.BarCodeReaderException("Could not find image path: %s" % filenames, filenames)
    elif stdout.startswith(b'''Exception in thread "main" java.io.IOException: Could not load '''):
        raise zxing.BarCodeReaderException("Java library could not read image; is it in a supported format?", filenames)
    elif stdout.startswith(b'''Exception '''):
        raise zxing.BarCodeReaderException("Unknown Java exception: %s" % stdout)
    elif process.returncode:
        raise zxing.BarCodeReaderException("Unexpected Java subprocess return code %d" % process.returncode, self.java)

    block_prefixes = (b"file:///", b"Exception")
    file_results = []
    for line in stdout.splitlines(True):
        if line.startswith(block_prefixes):
            file_results.append(line)
        elif file_results:
            file_results[-1] += line

    codes = [zxing.BarCode.parse(result) for result in file_results]
    if one_file:
        return codes[0] if codes else None

    found_codes = {code.uri: code for code in codes if code is not None}
    return [found_codes[file_uri] if file_uri in found_codes else None for file_uri in file_uris]


zxing.BarCode.parse = _safe_parse
zxing.BarCodeReader.decode = _safe_decode


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
