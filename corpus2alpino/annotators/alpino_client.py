#!/usr/bin/env python3
"""
Wrapper for the Alpino parser.
"""

import socket
import re
import os
import errno
import logging

from subprocess import run, PIPE
from datetime import date
from typing import List, Union, cast
from tempfile import TemporaryDirectory

from corpus2alpino.abstracts import Annotator
from corpus2alpino.models import Document, MetadataValue

closing_punctuation = re.compile(r'([^\s])([\.?!])$')
sentence_id_matcher = re.compile(r'(?<=sentid=")[^"]+(?=")')
sentence_tag_matcher = re.compile(r'(?<=<sentence)(?![\w-])')


def determine_alpino_version(alpino_directory: Union[str, None]):
    try:
        if alpino_directory == None:
            raise KeyError
        version_path = os.path.join(cast(str, alpino_directory), 'version')
        version = cast(Union[str, None], open(version_path).read().strip())
        version_date = cast(Union[date, None], date.fromtimestamp(
            os.path.getmtime(version_path)))
    except KeyError:
        version = None
        version_date = None
    return (version, version_date)


class AlpinoServerClient:
    """
    Wrapper for connecting to an Alpino parser server.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.prefix_id = True
        self.write_id = False
        parsed = self.parse_line("hallo wereld !", '42')
        if '"42|hallo"' in parsed:
            self.prefix_id = False  # Add it ourselves
            parsed = self.parse_line("hallo wereld !", '42')
            if not '"hallo"' in parsed:
                raise Exception("Alpino has unsupported sentence ID behavior")

        # validate that the match can be found
        match = sentence_id_matcher.search(parsed)
        if not match:
            # no sentence ID added, add it ourselves
            self.write_id = True
        else:
            if self.prefix_id and match.group(0) != "42":
                raise Exception(
                    "Unexpected sentence id: {0} instead of 42".format(match.group(0)))

        # detect version
        try:
            alpino_home = cast(Union[str, None], os.environ['ALPINO_HOME'])
        except KeyError:
            alpino_home = None
        self.version, self.version_date = determine_alpino_version(alpino_home)

    def parse_line(self, line: str, sentence_id: str) ->str:
        """Parse a line using the Alpino parser.


        Arguments:
            line {str} -- Tokenized text
            sentence_id {str} -- Id to record in the XML output

        Returns:
            {str} -- Lassy XML
        """

        # add a whitespace before the closing punctuation when it's missing
        line = closing_punctuation.sub(
            lambda m: m.group(1) + ' ' + m.group(2), line)

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

        if "<alpino_ds" not in xml:
            raise Exception(xml)

        if not self.prefix_id:
            xml = sentence_id_matcher.sub(sentence_id, xml)
        if self.write_id:
            xml = sentence_tag_matcher.sub(f" sentid=\"{sentence_id}\"", xml)

        return xml


class AlpinoProcessClient:
    """
    Wrapper for parsing using Alpino by running it as a process
    """

    def __init__(self, path: str, arguments: List[str]):
        """Initializes the parser

        Arguments:
            path {str} -- Path to the Alpino executable
            arguments {List{str}} -- Command line arguments to pass to the Alpino process
        """

        if os.path.isfile(path):
            # assume this is an extracted folder containing Alpino
            # ./bin/Alpino
            alpino_directory = os.path.split(os.path.split(path)[0])[0]
        else:
            if not os.path.isdir(path):
                # Path is neither a file or a directory:
                # it doesn't exist!
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), path)

            alpino_directory = path
            # assume path is the root of the Alpino folder
            path = os.path.join(path, "bin", "Alpino")

            if not os.path.isfile(path):
                raise FileNotFoundError(
                    errno.ENOENT, "Cannot find Alpino executable within specified path", path)

        self.path = path
        self.arguments = arguments
        self.version, self.version_date = determine_alpino_version(
            alpino_directory)

    def parse_line(self, line: str, sentence_id: str):
        """Parse a line using the Alpino parser.


        Arguments:
            line {str} -- Tokenized text
            sentence_id {str} -- Id to record in the XML output

        Returns:
            {str} -- Lassy XML
        """

        with TemporaryDirectory() as tmp:
            result = run([self.path, "-notk", "-end_hook=xml", "-flag", "treebank", tmp, "-parse"] + self.arguments,
                         input=f"{sentence_id}|{line}\n",
                         stdout=PIPE,
                         stderr=PIPE,
                         encoding="utf8")

            if result.stdout:
                logging.getLogger().warning(result.stdout)
            if result.stderr:
                logging.getLogger().warning(result.stderr)

            with open(os.path.join(tmp, f"{sentence_id}.xml"), "r", encoding="utf-8") as f:
                xml = f.read()
                return xml
