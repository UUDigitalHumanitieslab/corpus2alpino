#!/usr/bin/env python3
"""
Entry point for converting FoLiA xml files to Alpino XML files.
"""

import sys
import argparse
from folia2alpino.alpino_wrappers import AlpinoPassthroughWrapper, AlpinoServiceWrapper
from folia2alpino.converter import Converter

def main(args=None):
    """
    Main entry point.
    """
    if args is None:
        args = sys.argv[1:]

    try:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.HelpFormatter)

        parser.add_argument(
            'file_names', metavar='FILE', type=str, nargs='+', help='FoLiA file(s) to parse')
        parser.add_argument(
            '-s', '--server', metavar='SERVER', type=str, help='host:port of Alpino server')

        options = parser.parse_args(args)
        if options.server != None:
            [host, port] = options.server.split(":")
            converter = Converter(AlpinoServiceWrapper(host, int(port)))
        else:
            converter = Converter(AlpinoPassthroughWrapper())

        for chunk in converter.get_parses(options.file_names):
            print(chunk)

    except Exception as exception:
        sys.stderr.write(repr(exception) + "\n")
        sys.stderr.write("for help use --help\n\n")
        raise exception


if __name__ == "__main__":
    main()
