#!/usr/bin/env python3
"""
Module for automatically detecting the reader to use for a file
"""

from typing import Iterable

import ucto

from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue

from corpus2alpino.readers.chat import ChatReader
from corpus2alpino.readers.folia import FoliaReader
from corpus2alpino.readers.lassy import LassyReader
from corpus2alpino.readers.paqu import PaQuReader
from corpus2alpino.readers.tei import TeiReader


class AutoReader(Reader):
    """
    Class for reading a file in any supported format.
    """

    def __init__(self):
        tokenizer = ucto.Tokenizer("tokconfig-nld")
        self.readers = [ChatReader(), FoliaReader(tokenizer), LassyReader(), PaQuReader(tokenizer), TeiReader(tokenizer)]

    def read(self, file):
        for reader in self.readers:
            if reader.test_file(file):
                return reader.read(file)
        return []

    def test_file(self, file):
        for reader in self.readers:
            if reader.test_file(file):
                return True
        return False
