import os.path

from igor.binarywave import load as loadibw

import util


def ibw2dict(filename):
    """Extract the contents of an *ibw to a dict"""
    data = loadibw(filename)
    wave = data['wave']

    # Get the labels and tidy them up into a list
    labels = list(map(bytes.decode,
                      util.flatten(wave['labels'])))

    # Get the notes and process them into a dict
    notes = util.process_notes(wave['note'])

    # Get the data numpy array and convert to a simple list
    wData = wave['wData'].tolist()

    # Get the filename from the file - warn if it differs
    fname = wave['wave_header']['bname'].decode()
    input_fname = os.path.splitext(os.path.basename(filename))[0]
    if input_fname != fname:
        print("Warning: stored filename differs from input file name")
        print("Input filename: {}".format(input_fname))
        print("Stored filename: {}".format(str(fname) + " (.ibw)"))

    return {"filename": fname, "labels": labels, "notes": notes, "data": wData}


def ibw2stdout(filename):
    '''Dump the contents of an *.ibw to stdout'''
    data = loadibw(filename)
    util.pprint(data)
