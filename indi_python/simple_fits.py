#!/usr/bin/env python
"""
A very basic fits file parser. This only handles fits file
that contain a single (gray-scale) image. It was designed
primarily for the purpose of handling images from an 
INDI server.

Hazen 11/16
"""

import numpy


class SimpleFitsException(Exception):
    pass


def parseValue(string):
    """
    Try to convert a numeric string to an integer or a float.
    """
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            return string[1:-1]

        
class FitsImage(object):

    def __init__(self, fits_name = None, fits_string = None, verbose = True):
        self.keywords = {}
        self.np_data = None

#        if fits_name is None and fits_string is None:
#            raise SimpleFitsException("Must specify a fits file or a string containing a fits images.")

        if fits_name is not None:
            with open(fits_name, "rb") as fp:
                fits_string = fp.read()

        # Read out keywords:
        nkw = 0
        while True:

            record = fits_string[nkw*80:(nkw+1)*80]
            nkw += 1
            if verbose:
                print(record)

            if record.startswith(b'END'):
                break

            if record.startswith(b'COMMENT'):
                continue

            if (b'/' in record):
                record = record.split(b'/')[0]

            [keyword, value] = record.split(b'=')
            keyword = str(keyword.strip(), 'ascii')
            value = str(value.strip(), 'ascii')
            self.keywords[keyword] = parseValue(value)

        header_bytes = nkw*80

        # Find the start of the data (a multiple of 2880).
        data_start = 2880
        while (data_start < header_bytes):
            data_start += 2880

        # Check that this is not a color image.
        if ("NAXIS3" in self.keywords):
            raise SimpleFitsException("RGB image detected. Image type not set to 'RAW'?")
            
        # Determine image size.
        if ("NAXIS1" in self.keywords) and ("NAXIS2" in self.keywords):

            size1 = self.keywords["NAXIS1"]
            size2 = self.keywords["NAXIS2"]
            
            # Handle 16bit images.
            if (self.keywords["BITPIX"] == 16):
                if verbose:
                    print(size1, "x", size2, "- 16 bit image")

                # Calculate image size.
                image_size = size1 * size2 * 2

                # Create image.
                self.np_data = numpy.frombuffer(fits_string[data_start:data_start+image_size],
                                                dtype = numpy.dtype('>i2'))
                self.np_data = numpy.reshape(self.np_data, ((size2, size1)))

                # Add offset if specified. This will also convert to a 32 bit integer.
                if ("BZERO" in self.keywords):
                    self.np_data = self.np_data.astype(numpy.int32)
                    self.np_data += self.keywords["BZERO"]
                    self.keywords["BZERO"] = 0
                
                return

        raise SimpleFitsException("Unrecognized FITS file type")

    def getKeyword(self, keyword):
        return self.keywords[keyword]
        
    def getKeywords(self):
        return self.keywords

    def getImage(self):
        return self.np_data


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

    print("Image size is", fi.getImage().shape)


