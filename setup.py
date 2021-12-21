import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()


setuptools.setup(
    name="docbarcodes",
    version="1.0.9",
    author="Arlind Nocaj",
    author_email="nocaja.r@gmail.com",
    description="Docbarcodes extracts 1D and 2D barcodes from scanned PDF documents or images.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/docbarcodes",
    project_urls={
        "Bug Tracker": "https://github.com/ArlindNocaj/document-barcodes/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_dir={"docbarcodes": "docbarcodes"},
    packages=setuptools.find_packages(),
    install_requires=required,
    python_requires=">=3.6",
    entry_points={
        'console_scripts': ['docbarcodes=docbarcodes.cli:app'],
    },
    license_files=('LICENSE'),
)
