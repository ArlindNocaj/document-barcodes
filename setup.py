import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="docbarcodes",
    version="1.0.1",
    author="Arlind Nocaj",
    author_email="nocajar@gmail.com",
    description="Docbarcode extracts 1D and 2D barcodes from scanned PDF documents or images.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=required,
    dependency_links=[
          'http://github.com/ArlindNocaj/python-zxing/tarball/master#egg=python_zxing-0.13',
      ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': ['docbarcodes=docbarcodes.cli:app'],
    },
    include_package_data=True,
    license_files=('LICENSE'),
)