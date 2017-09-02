# ibw-extractor

Simple Python script for converting \*.ibw (Igor BinaryWave) files to CSV, TSV, or JSON, or dumping the contents to the terminal (stdout).

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
