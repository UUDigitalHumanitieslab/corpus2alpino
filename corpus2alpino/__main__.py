#!/usr/bin/env python3
"""
Entry point for converting FoLiA xml files to Alpino XML files.
"""

import sys
import argparse
from corpus2alpino.alpino_wrappers import AlpinoPassthroughWrapper, AlpinoServiceWrapper
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
            'file_names', metavar='FILE', type=str, nargs='+', help='FoLiA file(s) to parse')
        parser.add_argument(
            '-s', '--server', metavar='SERVER', type=str, help='host:port of Alpino server')
        parser.add_argument(
            '-o', '--output_file', metavar='OUTPUT', type=str, help='Output file')

        options = parser.parse_args(args)
        if options.server != None:
            [host, port] = options.server.split(":")
            converter = Converter(AlpinoServiceWrapper(host, int(port)))
        else:
            converter = Converter(AlpinoPassthroughWrapper())

        if options.output_file != None:
            output = FileOutput(options.output_file)
        else:
            output = ConsoleOutput()

        output.write(converter.get_parses(options.file_names))
        output.close()

    except Exception as exception:
        sys.stderr.write(repr(exception) + "\n")
        sys.stderr.write("for help use --help\n\n")
        raise exception


class FileOutput:
    """
    Output chunks to a file using newline separators.
    """

    def __init__(self, filename):
        self.file = open(filename, 'w', encoding='utf-8')

    def write(self, chunks):
        """
        Write all lines to the file.
        """
        self.file.writelines(chunk + '\n' for chunk in chunks)

    def close(self):
        """
        Release resources.
        """
        self.file.close()


class ConsoleOutput:
    """
    Output chunks to the console on separate lines.
    """

    def write(self, lines):
        """
        Write all lines to stdout.
        """
        for line in lines:
            print(line)

    def close(self):
        """
        Needed to have the same signature as FileOutput.
        """
        pass


if __name__ == "__main__":
    main()
