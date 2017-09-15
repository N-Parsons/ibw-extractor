import os.path
import json
import re
import csv

from pprint import pformat

import click


def save_to_file(content, filepath, mode="x", headers=False):
    """'Safe' interactive file saver - content should be a dict or string"""
    # Get the extension
    ext = os.path.splitext(filepath)[1]

    # Write the contents of the file, or ask for alternative filename
    try:
        with open(filepath, mode) as outfile:
            if ext == ".json":
                json.dump(content, outfile, indent=4, sort_keys=True)
            elif ext in {".csv", ".tsv"}:
                _delimiter = "," if ext == ".csv" else "\t"
                csvwriter = csv.writer(outfile, delimiter=_delimiter,
                                       quotechar='"',
                                       quoting=csv.QUOTE_NONNUMERIC)
                if headers:
                    data = content["labels"] + content["data"]
                else:
                    data = content["data"]
                for line in data:
                    csvwriter.writerow(line)
            else:
                outfile.write(content)
    except FileExistsError:
        click.secho("{} already exists!".format(filepath), fg="orange")
        if input("Do you want to overwrite it? (y/N): ").lower() == "y":
            save_to_file(content, filepath, mode="w", headers=headers)
        else:
            resp = input("Rename or cancel? (r/C): ")
            if resp == "r":
                new_filename = input("New filename ({}): ".format(ext))
                directory = os.path.dirname(filepath)
                new_filepath = os.path.join(directory, new_filename + ext)
                save_to_file(content, new_filepath, mode="x", headers=headers)
            else:
                click.secho("File not saved", fg="red")


def process_notes(notes):
    """Splits a byte string into an dict"""
    # Decode to UTF-8, split at carriage-return, and strip whitespace
    note_list = list(map(str.strip, notes.decode(errors='ignore').split("\r")))
    note_dict = dict(map(fill_blanks, [p.split(":") for p in note_list]))

    # Remove the empty string key if it exists
    try:
        del note_dict[""]
    except KeyError:
        pass
    return note_dict


def fill_blanks(lst):
    """Convert a list (or tuple) to a 2 element tuple"""
    try:
        return (lst[0], from_repr(lst[1]))
    except IndexError:
        return (lst[0], "")


def from_repr(s):
    """Get an int or float from its representation as a string"""
    # Strip any outside whitespace
    s = s.strip()
    # "NaN" and "inf" can be converted to floats, but we don't want this
    # because it breaks in Mathematica!
    if s[1:].isalpha():  # [1:] removes any sign
        rep = s
    else:
        try:
            rep = int(s)
        except ValueError:
            try:
                rep = float(s)
            except ValueError:
                rep = s
    return rep


def pprint(data):
    """
    Format things into lines to get nicer printing

    Function is taken from https://github.com/wking/igor/test/test.py"""
    lines = pformat(data).splitlines()
    print('\n'.join([line.rstrip() for line in lines]))


def flatten(lst):
    """Completely flatten an arbitrarily-deep list"""
    return list(_flatten(lst))


def _flatten(lst):
    """Generator for flattening arbitrarily-deep lists"""
    for item in lst:
        if isinstance(item, (list, tuple)):
            yield from _flatten(item)
        elif item not in (None, "", b''):
            yield item
