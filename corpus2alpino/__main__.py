#!/usr/bin/env python3
"""
Entry point for converting FoLiA xml files to Alpino XML files.
"""

import sys
import argparse

from corpus2alpino.annotators.alpino import AlpinoAnnotator
from corpus2alpino.collectors.filesystem import FilesystemCollector
from corpus2alpino.targets.filesystem import FilesystemTarget
from corpus2alpino.writers.lassy import LassyWriter

from corpus2alpino.converter import Converter


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
            'file_names', metavar='FILE', type=str, nargs='+', help='TEI/FoLiA file(s) to parse')
        parser.add_argument(
            '-s', '--server', metavar='SERVER', type=str, help='host:port of Alpino server')
        parser.add_argument(
            '-o', '--output_path', metavar='OUTPUT', type=str, help='Output path')
        parser.add_argument('-t', '--split_treebanks', action='store_true',
                            help='Split treebanks to separate files')

        parser.set_defaults(split_treebanks=False)

        options = parser.parse_args(args)

        converter = Converter(FilesystemCollector(options.file_names))
        if options.server != None:
            [host, port] = options.server.split(":")
            converter.annotators.append(AlpinoAnnotator(host, int(port), options.split_treebanks))
            converter.writer = LassyWriter(not options.split_treebanks)

        if options.output_path != None:
            converter.target = FilesystemTarget(options.output_path, not options.split_treebanks)

        converter.convert()

    except Exception as exception:
        sys.stderr.write(repr(exception) + "\n")
        sys.stderr.write("for help use --help\n\n")
        raise exception


if __name__ == "__main__":
    main()
