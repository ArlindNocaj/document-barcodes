
from docbarcodes.zxingjpype.zxingreader import decodeURIs

def test_jpype_qrcode():
    file = "data/single/qr-code-wikipedia.png"
    results = decodeURIs([file])
    assert results[0][0].text=='http://en.m.wikipedia.org'