#!/usr/bin/env python3
"""
Wrapper for the Alpino parser.
"""

import socket


class AlpinoServiceWrapper:
    """
    Wrapper for connecting to an Alpino parser server.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def parse_lines(self, lines):
        """
        Parse lines using the Alpino parser and wrap them in a treebank container.

        Arguments:

            strip: remove the xml header and remove the trailing newline
        """

        yield "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<treebank>"
        for line in lines:
            yield self.parse_line(line, True)
        yield "</treebank>"

    def parse_line(self, line, strip=False):
        """
        Parse a line using the Alpino parser.

        Arguments:

            strip: remove the xml header and remove the trailing newline
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.sendall((line + "\n\n").encode())
        received = []

        while True:
            buffer = s.recv(8192)
            if not buffer:
                break
            received.append(str(buffer, encoding='utf8'))

        total_xml = "".join(received)

        if strip:
            lines = total_xml.splitlines()
            lines = lines[1:]
            lines[-1] = lines[-1].rstrip()
            total_xml = "\n".join(lines)

        return total_xml


class AlpinoPassthroughWrapper:
    """
    Wrapper for passing through the strings which can be parsed using Alpino.
    """

    def parse_lines(self, lines):
        """
        Passthrough input.
        """

        return lines
