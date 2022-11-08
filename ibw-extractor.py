import os
import sys
import re

import click

import extractors
import util


VERSION = "0.1.3"


@click.command()
@click.argument('infiles', nargs=-1,
                type=click.Path(exists=True, resolve_path=True))
@click.option('--outfile', '-o', default=None, help="Output filename")
@click.option('--outformat', '-f', default=None, help="Output format",
              type=click.Choice(['csv', 'tsv', 'json', 'dump']))
@click.option('--outdir', '-d', default=None,
              help="Output file directory (relative to input file/folder)")
@click.option('--clobber', is_flag=True,
              help="Force overwrite without confirmation")
@click.option('--headers', is_flag=True,
              help="Include column headers in csv/tsv output")
@click.option('--recursive', is_flag=True,
              help="Recurse into sub-folders")
@click.option('--minimise', is_flag=True,
              help="Minimise JSON file size by removing structure")
@click.version_option(version=VERSION)
def main(infiles, outfile, outformat, outdir,
         clobber, headers, recursive, minimise):
    if not infiles:
        click.secho("No input files specified. Aborting.", fg="red")
        sys.exit(1)

    # Get/set writemode (x => create or ask, w => overwrite)
    writemode = "w" if clobber else "x"

    # Get the full list of input files
    if recursive:
        _infiles = list(filter(is_ibw, infiles))
        inpaths = filter(os.path.isdir, infiles)
        infiles = _infiles + recurse_subdirs(inpaths)
    else:
        infiles = util.flatten(map(list_ibw, infiles))

    # Check for errors
    if len(infiles) == 0:
        click.secho("No .ibw files found", fg="red")
        sys.exit(1)
    if len(infiles) > 1 and outfile:
        click.secho("Output filename cannot be " +
                    "specified for multiple input files", fg="red")
        sys.exit(1)

    # Iterate through input files and do action
    if outformat == "dump":
        for infile in infiles:
            extractors.ibw2stdout(infile)  # prints to stdout
    else:
        with click.progressbar(infiles, width=0) as bar:
            for infile in bar:
                outpath = get_outpath(infile, outfile, outformat, outdir)
                data = extractors.ibw2dict(infile)
                util.save_to_file(data, outpath, mode=writemode,
                                  csv_headers=headers, json_mini=minimise)


def recurse_subdirs(inpaths):
    """Recurse subdirectories and return a list of ibw files"""
    # inpaths may just be one element, so it needs to be forced into a list
    files = [os.path.join(d, f) for inpath in list(inpaths)
             for (d, _, fs) in os.walk(inpath)
             for f in fs]
    return util.flatten(filter(is_ibw, files))


def list_ibw(inpath):
    """List all of the *.ibw files in a given folder"""
    if is_ibw(inpath):
        files = [inpath]
    else:
        try:
            _files = os.listdir(inpath)
            files = list(filter(is_ibw, _files))
        except NotADirectoryError:
            files = []
    return files


def is_ibw(path):
    """Tests whether a file path has an '.ibw' extension"""
    return os.path.splitext(path)[1] == ".ibw"


def get_outpath(infile, outfile, outformat, outdir):
    """Uses the arguments to determine the output filename with some checks"""
    _dirname = os.path.dirname(infile)
    _basename = os.path.basename(infile)
    filename, in_ext = os.path.splitext(_basename)

    # Check that the input is an ibw
    if in_ext != ".ibw":
        click.secho("Input file does not have an .ibw extension", fg="red")
        sys.exit(1)

    # Get the output directory
    if outdir:
        file_dir = os.path.join(_dirname, outdir)
        os.makedirs(file_dir, exist_ok=True)  # make dirs in path if needed
    else:
        file_dir = _dirname

    # Get the output filename + extension
    if outfile:
        try:
            impl_ext = re.search(r'\.[^.\/]*$', outfile).group(0)
            if outformat and impl_ext[1:] != outformat:
                click.secho("Inconsistent formats in arguments", fg="red")
                sys.exit(1)
            else:
                file_name = outfile
        except AttributeError:  # No match found - no implied extension
            if outformat:
                file_name = outfile + "." + outformat
            else:
                click.secho("Output format not specified or implied", fg="red")
                sys.exit(1)
    elif outformat:
        file_name = filename + "." + outformat
    else:
        click.secho("Output format not specified or implied", fg="red")
        sys.exit(1)

    # Combine the components and return
    return os.path.join(file_dir, file_name)


if __name__ == "__main__":
    main()
