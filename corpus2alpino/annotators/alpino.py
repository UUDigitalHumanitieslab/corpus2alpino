#!/usr/bin/env python3
"""
Wrapper for the Alpino parser.
"""

ANNOTATION_KEY = 'alpino'

import socket
import re
import os

from datetime import date

from corpus2alpino.abstracts import Annotator
from corpus2alpino.models import Document, MetadataValue
from corpus2alpino.log import LogSingleton

closing_punctuation = re.compile(r'([^\s])([\.?!])$')
sentence_id_matcher = re.compile(r'(?<=sentid=")[^"]+(?=")')
timealign_symbol = re.compile(r'\u0015')


class AlpinoAnnotator(Annotator):

    """
    Wrapper for connecting to an Alpino parser server.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.prefix_id = True
        parsed = self.parse_line("hallo wereld !", '42')
        if '"42|hallo"' in parsed:
            self.prefix_id = False  # Add it ourselves
            parsed = self.parse_line("hallo wereld !", '42')
            if not '"hallo"' in parsed:
                raise Exception("Alpino has unsupported sentence ID behavior")

        # validate that the match can be found
        match = sentence_id_matcher.search(parsed)
        if not match:
            raise Exception(
                "No sentence id returned in XML structure by Alpino")

        if self.prefix_id and match.group(0) != "42":
            raise Exception(
                "Unexpected sentence id: {0} instead of 42".format(match.group(0)))

        # detect version
        if self.host == 'localhost':
            try:
                version_path = os.path.join(os.environ['ALPINO_HOME'], 'version')
                self.version = open(version_path).read().strip()
                self.version_date = date.fromtimestamp(os.path.getmtime(version_path))
            except KeyError:
                self.version = None
                self.version_date = None

    def annotate(self, document: Document):
        for utterance in document.utterances:
            try:
                # replace the symbol with a middot to prevent XML parsing errors
                utterance.annotations[ANNOTATION_KEY] = timealign_symbol.sub(
                    "·",
                    self.parse_line(utterance.text, utterance.id))
                if self.version:
                    utterance.metadata['alpino_version'] = MetadataValue(self.version)
                if self.version_date:
                    utterance.metadata['alpino_version_date'] = MetadataValue(self.version_date.isoformat(), 'date')
            except:
                LogSingleton.get().error(Exception("Problem parsing: {0}|{1}".format(utterance.id, utterance.text)))

    def parse_line(self, line, sentence_id):
        """
        Parse a line using the Alpino parser.

        Arguments:

            strip: remove the xml header and remove the trailing newline
        """

        # add a whitespace before the closing punctuation when it's missing
        line = closing_punctuation.sub(lambda m: m.group(1) + ' ' + m.group(2), line)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        if self.prefix_id:
            line = "{0}|{1}".format(sentence_id, line)
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

        return xml
