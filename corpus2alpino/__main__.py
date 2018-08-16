#!/usr/bin/env python3
"""
Entry point for converting FoLiA xml files to Alpino XML files.
"""

import sys
import argparse
from tqdm import tqdm

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
            'file_names', metavar='FILE', type=str, nargs='+',
            help='TEI/FoLiA file(s) to parse')
        parser.add_argument(
            '-s', '--server', metavar='SERVER', type=str,
            help='host:port of Alpino server')
        parser.add_argument(
            '-o', '--output_path', metavar='OUTPUT', type=str,
            help='Output path')
        parser.add_argument(
            '-p', '--progress', metavar="BOOL", type=bool,
            help='Show progress bar, automatically turned on file output')
        parser.add_argument('-t', '--split_treebanks', action='store_true',
                            help='Split treebanks to separate files')

        parser.set_defaults(split_treebanks=False)

        options = parser.parse_args(args)

        collector = FilesystemCollector(options.file_names)
        converter = Converter(collector)
        if options.server != None:
            [host, port] = options.server.split(":")
            converter.annotators.append(AlpinoAnnotator(host, int(port)))
            converter.writer = LassyWriter(not options.split_treebanks)

        if options.output_path != None:
            converter.target = FilesystemTarget(
                options.output_path, not options.split_treebanks)

        show_progress = options.progress if options.progress != None else options.output_path != None

        if show_progress:
            with tqdm(converter.convert(), total=len(options.file_names), unit='file') as progress:
                last = collector.position
                for _ in converter.convert():
                    progress.update(collector.position - last)
                    last = collector.position
                    progress.total = collector.total
        else:
            for _ in converter.convert():
                pass

    except Exception as exception:
        sys.stderr.write(repr(exception) + "\n")
        sys.stderr.write("for help use --help\n\n")
        raise exception


if __name__ == "__main__":
    main()
