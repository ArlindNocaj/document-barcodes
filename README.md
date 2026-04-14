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

1. Detect barcode regions on the document using opencv and [image transformation heuristics](https://github.com/pyxploiter/Barcode-Detection-and-Decoding)
2. Extract the raw barcode data using [zxing](https://github.com/zxing/zxing)
3. Combine multiple barcodes and decode the data.


# Quick start 

Required:
* Java 8

Install package
  
```
pip install docbarcodes
```

Download example pdf document
```
wget https://github.com/ArlindNocaj/document-barcodes/raw/master/data/salary_swissdec/SalarySinglePage.pdf 
```

## CLI usage
Extract barcodes from salary statement document and format result json using `jq`.

```shell
docbarcodes ./SalarySinglePage.pdf | jq .
```
```yaml
{
  "BarcodesRaw": [
    {
      "page": 0,
      "num_candidate": 2,
      "raw": "´cý¸z\u0000\u0002V\u0001\u0003\u0000\u0001\u0000\u0001PK\u0003\u0004\u0014\u0000\b\b\b\u0000év\u0003Q\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0004\u0000\u0000\u0000txabMÝnâ0\u0010_Åò}b;¡!¬\u001cWá¯EbYÔÐjÕ;\u0013Ü\u00105±+Û,ð>û&ûb;\tÐö\"Îñ\u0019Ïçùý©mÐ\u001fe]mtYH1Rº4»ZW\u0019~ÞÌ\u0014ß\u000b¾A¦]÷Þ\u007fü äx<îX;·SeXî+÷ªÄíHD#J£B6Ò§ªôpúæ1*\u0016Ó\fS\nm³{é$ÃOLû!õ\u0019=/¦Áx^dxò8\u000bX\u0014×\u000f£5 vkyh$Z)ç\u001be1z|\n&ÁJ¶\nj~ý\\/g¿Ñ¬QïÞ\u001a]¿£ü\u0001£×Å:ÃqÒµ,3o½ª®PáÕAYPJ\u0003·Jù\fÏêJÙ£ªP\u0002=ó[s±D\u0003(®ý9Ãý\u0001²×{£¡#c\u0014Å)\u001aÐa\"ør1EKé¼î©rµ1×öÓÐZÞ¨èê\u000b`ùï¯®*éó\u0016V¢ï$É\b\n¦MOs£\u001a+«Ñ\bvæ ½í\u0002\u0017/A^\u0004++º\u0019\u000eîa(\u000b£Ï\u0010'7bÁsÁ§¦\u0004Å8¹î:µÙ\tþfM+\"ÊÑB¼78ôª«ÏrrqúSûÂ\u0005<¥VAÊX\u001a\u000e!ájð\u0007k»n\u0014Æ\u0010R~wùJù«¼KâAÜ'|y\u0000/ÙÿPK\u0007\bK¦nJÎ\u0001\u0000\u0000Á\u0002\u0000\u0000PK\u0001\u0002\u0014\u0000\u0014\u0000\b\b\b\u0000év\u0003QK¦nJÎ\u0001\u0000\u0000Á\u0002\u0000\u0000\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000txabPK\u0005\u0006\u0000\u0000\u0000\u0000\u0001\u0000\u0001\u00002\u0000\u0000\u0000\u0000\u0002\u0000\u0000\u0000\u0000",
      "format": "PDF_417",
      "points": [
        [
          0.08509771986970684,
          0.2564102564102564
        ],
        [
          0.32166123778501626,
          0.2564102564102564
        ],
        [
          0.32166123778501626,
          0.35522904062229904
        ],
        [
          0.08509771986970684,
          0.35522904062229904
        ]
      ],
      "resultMetadata": {
        "ERROR_CORRECTION_LEVEL": "2",
        "PDF417_EXTRA_METADATA": {
          "addressee": "None",
          "checksum": -1,
          "fileId": "None",
          "fileName": "None",
          "fileSize": -1,
          "optionalData": "None",
          "segmentCount": -1,
          "segmentIndex": 0,
          "sender": "None",
          "timestamp": -1
        }
      }
    }
  ],
  "BarcodesCombined": [
    {
      "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><T xmlns=\"http://www.swissdec.ch/schema/sd/20200220/SalaryDeclarationTxAB\" SID=\"000\" SysV=\"001\"><Company UID-BFS=\"CHE-123.123.123\" Person=\"Paula Nestler\" HR-RC-Name=\"COMPLEX Elektronik AG\" ZIP=\"3600\" CL=\"Abteilung Steuerungen\" Street=\"Eigerweg 6\" Postbox=\"124\" City=\"Thun\" Phone=\"033 238 49 71\"/><PersonID Lastname=\"Aebi\" Firstname=\"Anna\" ZIP=\"3000\" CL=\"\" Street=\"LÃ¤nggassstrasse 26\" Postbox=\"690\" Locality=\"\" City=\"Bern 9\" Country=\"\"><SV-AS-Nr>123.4567.8901.28</SV-AS-Nr></PersonID><A><DocID>1</DocID><Period><from>2016-10-01</from><until>2016-11-30</until></Period><Income>48118.70</Income><GrossIncome>68000.00</GrossIncome><NetIncome>56343.00</NetIncome></A></T>",
      "format": "PDF_417",
      "sources": [
        0
      ]
    }
  ]
}
```
## Code Usage

```python
from docbarcodes.extract import process_document

barcodes_raw, barcodes_combined = process_document("./SalarySinglePage.pdf")

print(barcodes_raw)
print(barcodes_combined)
```

# FAQ

PDF rendering is handled by `pypdfium2`, which bundles its own PDFium binary — no external poppler installation is required.


# Show package licenses

```
pip-licenses --with-urls --with-system --format=markdown
```

# Improvements to be made:

* [ ] implement multithreading class for zxing in java which returns proper objects for python consumption
* [ ] extension mechanisms for other 2D barcode aggregations
