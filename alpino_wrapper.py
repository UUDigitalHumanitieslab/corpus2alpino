#!/usr/bin/env python3
"""
Wrapper for the Alpino parser.
"""

import socket


class AlpinoWrapper:
    """
    Wrapper for connecting to an Alpino parser server.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def parse(self, line, strip):
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
