#!/usr/bin/env python3
"""
Wrapper for the Alpino parser.
"""

from xml.sax.saxutils import escape
import socket
import re

sentence_id_matcher = re.compile(r'(?<=sentid=")[^"]+(?=")')

class AlpinoServiceWrapper:
    """
    Wrapper for connecting to an Alpino parser server.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.prefix_id = True
        parsed = self.parse_line("hallo wereld !", '42', {})
        if '"42|hallo"' in parsed:
            self.prefix_id = False # Add it ourselves
            parsed = self.parse_line("hallo wereld !", '42', {})
            if not '"hallo"' in parsed:
                raise Exception("Alpino has unsupported sentence ID behavior")
        
        # validate that the match can be found
        match = sentence_id_matcher.search(parsed)
        if not match:
            raise Exception("No sentence id returned in XML structure by Alpino")
        
        if self.prefix_id and match.group(0) != "42":
            raise Exception(f"Unexpected sentence id: {match.group(0)} instead of 42")

    def parse_lines(self, lines):
        """
        Parse lines using the Alpino parser and wrap them in a treebank container.

        Arguments:

            strip: remove the xml header and remove the trailing newline
        """

        yield "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<treebank>"
        for (line, sentence_id, metadata) in lines:
            yield self.parse_line(line, sentence_id, metadata, True)
        yield "</treebank>"

    def parse_line(self, line, sentence_id, metadata, strip=False):
        """
        Parse a line using the Alpino parser.

        Arguments:

            strip: remove the xml header and remove the trailing newline
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        if self.prefix_id:
            line = f"{sentence_id}|{line}"
        s.sendall((line + "\n\n").encode())
        received = []

        while True:
            buffer = s.recv(8192)
            if not buffer:
                break
            received.append(str(buffer, encoding='utf8'))

        xml = "".join(received)

        if not self.prefix_id:
            xml = sentence_id_matcher.sub(sentence_id, xml)

        lines = xml.splitlines()

        if metadata:
            lines.insert(-1, self.render_metadata(metadata))

        if strip:
            lines = lines[1:]
            lines[-1] = lines[-1].rstrip()

        return "\n".join(lines)

    def render_metadata(self, metadata):
        return "<metadata>\n" + "\n".join(
            f'<meta type="text" name="{key}" value="{self.escape_xml_attribute(value)}" />' for (key, value) in metadata.items()
        ) + "\n</metadata>"

    def escape_xml_attribute(self, value):
        return escape(value).replace('\n', '&#10;').replace('\r', '')

class AlpinoPassthroughWrapper:
    """
    Wrapper for passing through the strings which can be parsed using Alpino.
    """

    def parse_lines(self, lines):
        """
        Passthrough input.
        """

        return lines
