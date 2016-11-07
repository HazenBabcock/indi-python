#!/usr/bin/env python
"""
A very basic fits file parser. This only handles fits file
that contain a single (gray-scale) image.

Hazen 11/16
"""

import numpy


class SimpleFitsException(Exception):
    pass


class FitsImage(object):

    def __init__(self, fits_name = None, fits_string = None):
        self.keywords = {}
        self.np_data = None

        if fits_name is None and fits_string is None:
            raise SimpleFitsException("Must specify a fits file or a string containing a fits images.")

        if fits_name is not None:
            with open(fits_name, "rb") as fp:
                fits_string = fp.read()

        # Read out keywords:
        while not fits_string.startswith(b'END'):

            record = fits_string[:80]
            fits_string = fits_string[80:]
            
            if record.startswith(b'COMMENT'):
                continue

            if (b'/' in record):
                record = record.split(b'/')[0]

            [keyword, value] = record.split(b'=')
            keyword = keyword.strip()
            value = value.strip()
            self.keywords[keyword] = value

        fits_string = fits_string[80:]
        
        # Determine image size
        
    def getKeyword(self, keyword):
        return self.keywords[keyword]
        
    def getKeywords(self):
        return self.keywords
                

if (__name__ == "__main__"):

    import argparse

    parser = argparse.ArgumentParser(description = 'A (simple) FITS format parser')

    parser.add_argument('--fits_file', dest='fits_file', type=str, required=True,
                        help = "The name of the fits file to load.")

    args = parser.parse_args()

    fi = FitsImage(fits_name = args.fits_file)
    print("This file has the following keywords:")
    for key in fi.getKeywords():
        print(" ", key, fi.getKeyword(key))
    print("")
