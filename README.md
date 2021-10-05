[![Build and Test](https://github.com/ArlindNocaj/document-barcodes/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/ArlindNocaj/document-barcodes/actions/workflows/python-package-conda.yml)

# Intro

Barcodes are being used in many documents or forms to enable machine reading capabilities and reduce manual processing effort.
Simple 1D barcodes for example can mark a specific page on a form, or indicate a relevant document identification number.
More complex 2D barcodes allow to encode even the full data of the document in a more structured form.

Docbarcodes extracts 1D and 2D barcodes from scanned PDF documents or images.
It can be used to automate extraction and processing of all kind of documents.

Some working documents with barcodes are:

* Swiss tax statements (Zurich, other cantons can be added as well)
* Swiss salary statement  
* US drivers licenses with MRZ (machine readable zone)
* Swiss QR Code Invoices, introduced by [Six-group](https://www.six-group.com/en/newsroom/media-releases/2020/20200609-qr-bill-launch.html) 
* Swiss Covid Certificates

The approach works as follows:

1. Detect barcode regions on the document using opencv and image transformation heuristics, see https://github.com/pyxploiter/Barcode-Detection-and-Decoding
2. Extract the raw barcode data using [zxing](https://github.com/zxing/zxing)
3. Combine multiple barcodes and decode the data.


# Usage 

[ ] Extract zurich tax statements

[ ] Extract swiss salary statement


# Show package licenses

```
pip-licenses --with-urls --with-system --format=markdown
```

# Limitations


# TODO:

* [x] implement convert pdf to images
* [x] implement detect 2D barcode
* [x] implement extract 2D barcodes raw text (Java)
* [x] implement combine raw 2D barcodes
* [ ] extension mechanisms for other 2D barcode aggregations
* [x] finalize output format, needs to be nice for long term solution to provide pdf417 metadata
* [x] replace py-zxing (cmd hack and parse) with Jpype -> zxing calling (1 object class, and one caller to zxing)
* [x] finish multiresolution barcode extraction
* [ ] write test for barcode detection
* [x] write test for ZH extraction 
* [x] clean up temp files and images to avoid out of space issues
* [x] refactor and document project: needs to be written in a nicer way so that its easy understandable
* [x] add swiss invoice QR document sample and test
* [x] implement jpype tests for connector
* [x] command line interface for library
* [x] fix jpype problem for singleSalarystatement (only partial data got extracted)
* [x] list licenses of used projects
* [ ] add code usage examples for ZH statements to Readme
* [ ] add code usage examples for Salary statements to Readme
