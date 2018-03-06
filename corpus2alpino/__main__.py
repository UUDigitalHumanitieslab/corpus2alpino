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
        parser.add_argument('-t', '--split_treebanks', action='store_true', help='Split treebanks to separate files')

        parser.set_defaults(split_treebanks=False)

        options = parser.parse_args(args)
        if options.server != None:
            [host, port] = options.server.split(":")
            converter = Converter(AlpinoServiceWrapper(host, int(port), options.split_treebanks))
        else:
            converter = Converter(AlpinoPassthroughWrapper())

        if options.output_file != None:
            output = FileOutput(options.output_file, options.split_treebanks)
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

    def __init__(self, filename, split_treebanks):
        self.filename = filename
        self.index = 1
        self.split_treebanks = split_treebanks

        if not self.split_treebanks:
            # using a single file
            self.file = open(filename, 'w', encoding='utf-8')
        else:
            self.file = None

    def write(self, parsed_lines):
        """
        Write all lines to the file.
        """

        if self.split_treebanks:
            for parsed_line in parsed_lines:
                # using a separate file for each parse
                if self.file != None:
                    self.file.close()

                self.file = open(self.filename.replace('.txt', f'-{self.index}.txt').replace('.xml', f'-{self.index}.xml'), 'w', encoding='utf-8')        
                self.index += 1
                self.file.write(parsed_line + '\n')
        else:
            self.file.writelines(parsed_line + '\n' for parsed_line in parsed_lines)


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
