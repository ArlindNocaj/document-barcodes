import tempfile
from loguru import logger
from pdf2image import convert_from_path
from pathlib import Path
import os


def convert_pdf_to_images(file_path, last_page=None):
    """
    Converts a pdf document to images up to the defined last page.
    :param file_path:
    :param last_page:
    :return:
    """
    p = Path(file_path)

    with tempfile.TemporaryDirectory() as outpath:
        logger.debug('created temporary directory', outpath)
        os.makedirs(outpath, exist_ok=True)
        logger.info(f"converting pdf to images: {file_path} to {outpath}")
        images_from_path = convert_from_path(file_path, dpi=600, output_folder=outpath,
                                             output_file=str(p.stem), fmt="jpeg", last_page=last_page)
        logger.info(f"num pages: {len(images_from_path)}")
        return images_from_path
