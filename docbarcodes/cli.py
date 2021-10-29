import json
from pathlib import Path
from typing import List

from loguru import logger
import typer
from docbarcodes.extract import process_document
# from docbarcodes.zxingjpype.zxingreader import buildHints
import sys
app = typer.Typer()



@app.command()
def extract(files: List[Path], try_harder: bool = False, possible_formats = ["PDF_417", "CODE_128", "QR_CODE", "AZTEC"], verbose: bool = typer.Option(False, "--verbose"), hex: bool = typer.Option(False, "--hex", help="outputs the raw barcodes as hex")):

    if not verbose:
        logger.remove()
        logger.add(sys.stderr, level="ERROR")

    for path in files:
        if not path.is_file():
            typer.echo(f"File does not exists: {path.name}")

        raw, combined = process_document(str(path), try_harder=try_harder, possible_formats = possible_formats)

        raw_dict = [b._asdict() for b in raw]
        combined_dict = [b._asdict() for b in combined]

        response = {"BarcodesRaw": raw_dict, "BarcodesCombined": combined_dict}

        if not hex:
            typer.echo(json.dumps(response))

        if hex:
            for barcode in raw:
                if isinstance(barcode.raw,str):
                    typer.echo(barcode.raw.encode("ISO-8859-1").hex().upper())
                else:
                    typer.echo(barcode.raw)
if __name__ == "__main__":
    app()