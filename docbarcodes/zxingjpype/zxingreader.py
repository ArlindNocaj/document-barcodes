import cv2
import jpype
from jpype.types import *
import jpype.imports
import pathlib
import os
import multiprocessing
from loguru import logger

# zxing libraries are part of the package next to the python file
if not jpype.isJVMStarted():
    jar_path = os.path.join(pathlib.Path(os.path.realpath(__file__)).parent, "jars/*")
    #     logger.debug(f"jar_path: {jar_path}")
    #     logger.debug("starting JVM")
    jpype.startJVM(jpype.getDefaultJVMPath(), '-Djava.awt.headless=true', classpath=[jar_path], convertStrings=False)

import java
# print(java.lang.System.getProperty('java.class.path'))
# print(jpype.getClassPath())
import os
from com.google.zxing import BinaryBitmap
from com.google.zxing import MultiFormatReader
from com.google.zxing.common import HybridBinarizer
from com.google.zxing.multi import GenericMultipleBarcodeReader
from com.google.zxing.client.j2se import BufferedImageLuminanceSource
from com.google.zxing.client.j2se import ImageReader
import com.google.zxing.pdf417.PDF417ResultMetadata
from java.net import URI
from com.google.zxing.client.j2se import CommandLineRunner
from java.lang import System
import com.google.zxing.pdf417.PDF417ResultMetadata

from com.google.zxing import DecodeHintType
from com.google.zxing import BarcodeFormat
from javax.imageio import ImageIO
from java.util import EnumMap
from java.io import ByteArrayInputStream
import com.google.zxing.NotFoundException


def possible_formats():
    return list(java.util.Arrays.asList(BarcodeFormat.values()))


def buildHints(try_harder=False, possible_formats=None, pure_barcode=False, products_only=False):
    finalPossibleFormats = JClass('java.util.ArrayList')()

    if possible_formats is not None and len(possible_formats) > 0:
        for format in possible_formats:
            try:
                enum = BarcodeFormat.valueOf(format)
                finalPossibleFormats.add(enum)
            except java.lang.Exception as exception:
                formats = java.util.Arrays.asList(BarcodeFormat.values())
                logger.info(f"ignoring barcode format {format}, supported formats: {str(formats)}")

    else:
        finalPossibleFormats.add(BarcodeFormat.UPC_A),
        finalPossibleFormats.add(BarcodeFormat.UPC_E),
        finalPossibleFormats.add(BarcodeFormat.EAN_13),
        finalPossibleFormats.add(BarcodeFormat.EAN_8),
        finalPossibleFormats.add(BarcodeFormat.RSS_14),
        finalPossibleFormats.add(BarcodeFormat.RSS_EXPANDED)

        if not products_only:
            finalPossibleFormats.add(BarcodeFormat.CODE_39)
            finalPossibleFormats.add(BarcodeFormat.CODE_93)
            finalPossibleFormats.add(BarcodeFormat.CODE_128)
            finalPossibleFormats.add(BarcodeFormat.ITF)
            finalPossibleFormats.add(BarcodeFormat.QR_CODE)
            finalPossibleFormats.add(BarcodeFormat.DATA_MATRIX)
            finalPossibleFormats.add(BarcodeFormat.AZTEC)
            finalPossibleFormats.add(BarcodeFormat.PDF_417)
            finalPossibleFormats.add(BarcodeFormat.CODABAR)
            finalPossibleFormats.add(BarcodeFormat.MAXICODE)

    hints = JClass('java.util.HashMap')()
    # hints = EnumMap()
    hints.put(DecodeHintType.POSSIBLE_FORMATS, finalPossibleFormats)
    if try_harder:
        hints.put(DecodeHintType.TRY_HARDER, java.lang.Boolean.TRUE)

    if pure_barcode:
        hints.put(DecodeHintType.PURE_BARCODE, java.lang.Boolean.TRUE)

    return hints


class PDF417ResultMetadata:
    segmentIndex = -1
    fileId = None
    lastSegment = -1
    segmentCount = -1
    sender = None
    addressee = None
    fileName = None
    fileSize = -1
    timestamp = -1
    checksum = -1
    optionalData = None

    def __init__(self, dict):
        if not isinstance(dict, com.google.zxing.pdf417.PDF417ResultMetadata):
            return

        self.addressee = str(dict.getAddressee())
        self.checksum = int(dict.getChecksum())
        self.fileId = str(dict.getFileId())
        self.fileName = str(dict.getFileName())
        self.fileSize = int(dict.getFileSize())
        self.optionalData = str(dict.getOptionalData())
        self.segmentCount = int(dict.getSegmentCount())
        self.segmentIndex = int(dict.getSegmentIndex())
        self.sender = str(dict.getSender())
        self.timestamp = int(dict.getTimestamp())

    def __str__(self):
        output = ""
        for _, var in vars(self).items():  # Iterate over the values
            output += str(var)  # Use the str() function here to make the object return its string form
        return output


def convertJObject(obj):
    objMap = {}
    for i in dir(obj):
        if i.startswith("get"):
            name = i.split("get")[1]
            v = getattr(obj, i)()
            converted = convertJType(v)
            objMap[name] = converted
    return objMap


def convertJType(val):
    import java
    if val is None:
        return None
    elif isinstance(val, JInt) or isinstance(val, JLong):
        return int(val)
    elif isinstance(val, java.lang.String):
        return str(val)
    else:
        return str(val)


class Result:
    def __str__(self):
        return f"format: {repr(self.format)} ,text {repr(self.text)}" \
               f",rawBytes: {repr(self.rawBytes)} " \
               f",meta: {[(key, str(val)) for key, val in self.resultMetadata.items()]}"

    def __init__(self, result):
        self.text = str(result.getText())
        self.rawBytes = str(result.getRawBytes())
        self.numBits = int(result.getNumBits())
        self.resultPoints = [(p.getX(), p.getY()) if p is not None else None for p in result.getResultPoints()]
        self.format = str(result.getBarcodeFormat())

        metaData = {}
        self.timestamp = int(result.getTimestamp())

        if result.getResultMetadata() is None:
            self.resultMetadata = {}
            return

        for e in result.getResultMetadata().entrySet():
            key = e.getKey()
            key = str(key)
            obj = e.getValue()
            if isinstance(obj, com.google.zxing.pdf417.PDF417ResultMetadata):
                # obj = convertJObject(obj)
                obj = PDF417ResultMetadata(obj)
            else:
                obj = convertJType(obj)
            metaData[key] = obj
        self.resultMetadata = metaData


def _decodeImage(image_cv2, hints):
    is_success, im_buf_arr = cv2.imencode(".jpg", image_cv2)
    byte_im = im_buf_arr.tobytes()
    image = ImageIO.read(ByteArrayInputStream(byte_im))
    # image = ImageReader.readImage(uri)
    source = BufferedImageLuminanceSource(image)
    hb = HybridBinarizer(source)
    bitmap = BinaryBitmap(hb)
    multiFormatReader = MultiFormatReader()
    reader = GenericMultipleBarcodeReader(multiFormatReader)
    try:
        run_results = reader.decodeMultiple(bitmap, hints)
    except com.google.zxing.NotFoundException as exception:
        run_results = []
        pass
    myres = [Result(res) for res in run_results]
    return myres


def decodeImages(cv2_images, try_harder=True, possible_formats=None,
                 pure_barcode=False, products_only=False):
    """
    Extracts barcodes of a list of cv2 image objects by converting them to byte array and passing the byte array to
    Benefit of this method is that it provides additional meta data for e.g. PDF417 which can be used to merge multiple barcode chunks together.
    :param cv2_images:
    :param try_harder:
    :param possible_formats:
    :param pure_barcode:
    :param products_only:
    :return:
    """
    hints = buildHints(try_harder, possible_formats, pure_barcode, products_only)

    results = []
    for image in cv2_images:
        barcode_file = "./adad.jpg"
        myres = _decodeImage(image, hints)
        results.append(myres)
    return results


def decodeURIs(uris, try_harder=True, possible_formats=None,
               pure_barcode=False, products_only=False):
    """
    Extracts barcodes of a list of URIS, e.g. local files or base64 encoded data, https://en.wikipedia.org/wiki/Data_URI_scheme
    Benefit of this method is that it provides additional meta data for e.g. PDF417 which can be used to merge multiple barcode chunks together.
    :param uris:
    :param try_harder:
    :param possible_formats:
    :param pure_barcode:
    :param products_only:
    :return:
    """

    hints = buildHints(try_harder, possible_formats, pure_barcode, products_only)

    if isinstance(uris, str):
        file_uris = [pathlib.Path(uris).absolute().as_uri()]
    else:
        file_uris = [pathlib.Path(f).absolute().as_uri() for f in uris]

    # print(System.getProperty("java.class.path"))
    results = []
    for f in file_uris:
        uri = URI(f)
        # return ImageIO.read(new ByteArrayInputStream(imageBytes))
        image = ImageReader.readImage(uri)
        source = BufferedImageLuminanceSource(image)
        hb = HybridBinarizer(source)
        bitmap = BinaryBitmap(hb)
        multiFormatReader = MultiFormatReader()
        reader = GenericMultipleBarcodeReader(multiFormatReader)
        # results = reader.decodeMultiple(bitmap, hints)
        try:
            run_results = reader.decodeMultiple(bitmap, hints)
        except com.google.zxing.NotFoundException:
            run_results = []
            pass
        myres = [Result(res) for res in run_results]
        results.append(myres)
    return results


if __name__ == "__main__":
    filenames = ["./data/pdf417-metadata.png",
                 "./data/swiss_qr_bill_en_sample.png"]
    jar_path = "./src/docbarcodes/jars/*"

    image = cv2.imread('./data/pdf417-metadata.png')

    results = decodeImages([image])

    for item in results:
        for r in item:
            print(r)