import os
import re

import click

import extractors
import util


VERSION = "0.1.2-dev"


class ArgumentError(Exception):
    pass


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
@click.version_option(version=VERSION)
def main(infiles, outfile, outformat, outdir, clobber, headers, recursive):
    # Get/set writemode (x => create or ask, w => overwrite)
    writemode = "w" if clobber else "x"

    # Get the full list of input files
    if recursive:
        _infiles = list(filter(os.path.isfile, infiles))
        inpaths = filter(os.path.isdir, infiles)
        infiles = _infiles + recurse_subdirs(inpaths)
    else:
        infiles = util.flatten(map(list_ibw, infiles))

    # Check for errors
    if len(infiles) is 0:
        raise ArgumentError("No valid input files found")
    if len(infiles) > 1 and outfile:
        raise ArgumentError("Output filename cannot be \
                            specified for multiple input files")

    # Iterate through input files and do action
    if outformat == "dump":
        for infile in infiles:
            extractors.ibw2stdout(infile)  # prints to stdout
    else:
        with click.progressbar(infiles) as bar:
            for infile in bar:
                outpath = get_outpath(infile, outfile, outformat, outdir)
                data = extractors.ibw2dict(infile)
                util.save_to_file(data, outpath, mode=writemode)


def recurse_subdirs(inpaths):
    """Recurse subdirectories and list return a list of ibw files"""
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
        raise ArgumentError("Input file does not have a .ibw extension")

    # Get the output directory
    if outdir:
        file_dir = os.path.join(_dirname, outdir)
        os.mkdirs(file_dir, exist_ok=True)  # make dirs and subdirs (if needed)
    else:
        file_dir = _dirname

    # Get the output filename + extension
    if outfile:
        try:
            impl_ext = re.search(r'\.[^.\/]*$', outfile).group(0)
            if outformat and impl_ext[1:] != outformat:
                raise ArgumentError("Inconsistent formats in arguments")
            else:
                file_name = outfile
        except AttributeError:  # No match found - no implied extension
            if outformat:
                file_name = outfile + "." + outformat
            else:
                raise ArgumentError("Output format not specified or implied")
    elif outformat:
        file_name = filename + "." + outformat
    else:
        raise ArgumentError("Output format not specified or implied")

    # Combine the components and return
    return os.path.join(file_dir, file_name)


if __name__ == "__main__":
    main()
