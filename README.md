# ibw-extractor

A Python-based commandline tool for converting \*.ibw (Igor BinaryWave) files to CSV, TSV, or JSON, or dumping the contents to the terminal.

## Dependencies:
This package depends on `igor`, `click`, and `numpy`. The optional dependencies for `igor`, namely `matplotlib` and `nose`, are not required or utilised by this package.

**Suggested command:** `pip install igor click numpy`

**Package dependencies:**
* igor == 0.3 ([GitHub](https://github.com/wking/igor), [PyPI](https://pypi.python.org/pypi/igor))
* click >= 6.0 ([GitHub](https://github.com/pallets/click), [PyPI](https://pypi.python.org/pypi/click))
* numpy ([PyPI](https://pypi.python.org/pypi/numpy))

This package has been tested with Python 3.4 and 3.6, and so should be expected to work with **Python >= 3.4**, but may work with other versions. If you would like to extend compatibility, please submit a pull request.

## Usage:
```
$ python ibw-extractor.py --help

Usage: ibw-extractor.py [OPTIONS] [INFILES]...

Options:
  -o, --outfile TEXT              Output filename
  -f, --outformat [csv|tsv|json|dump]
                                  Output format
  -d, --outdir TEXT               Output file directory (relative to input
                                  file/folder)
  --clobber                       Force overwrite without confirmation
  --headers                       Include column headers in csv/tsv output
  --recursive                     Recurse into sub-folders
  --help                          Show this message and exit.
```
