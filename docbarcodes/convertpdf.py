from loguru import logger
import pypdfium2 as pdfium


def convert_pdf_to_images(file_path, last_page=None):
    """
    Converts a pdf document to images up to the defined last page.
    :param file_path:
    :param last_page:
    :return:
    """
    logger.info(f"converting pdf to images: {file_path}")
    pdf = pdfium.PdfDocument(file_path)
    try:
        n_pages = len(pdf)
        if last_page is not None:
            n_pages = min(n_pages, last_page)

        images = []
        for i in range(n_pages):
            page = pdf[i]
            try:
                bitmap = page.render(scale=600 / 72)
                pil_image = bitmap.to_pil()
                images.append(pil_image)
            finally:
                page.close()
    finally:
        pdf.close()

    logger.info(f"num pages: {len(images)}")
    return images
