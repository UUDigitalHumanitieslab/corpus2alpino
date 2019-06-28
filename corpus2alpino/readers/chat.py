#!/usr/bin/env python3
"""
Module for reading CHAT cha files to parsable utterances.
"""
from typing import Dict, Iterable, List, Tuple
from chamd import ChatReader as ChatParser

import os
import re
import ucto

from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance

class ChatReader(Reader):
    """
    Class for converting a CHAT file to document.
    """

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        self.reader = ChatParser()
        chat = self.reader.read_string(collected_file.content, collected_file.filename)
        yield Document(collected_file,
            list(self.parse_utterances(chat.lines)),
            self.parse_metadata(chat.metadata))

    def parse_utterances(self, chat_lines):
        for line in chat_lines:
            yield Utterance(line.text,
                 str(line.uttid),
                 self.parse_metadata(line.metadata),
                 int(line.metadata['uttstartlineno'].text))

    def parse_metadata(self, metadata):
        parsed = {}
        for (key, item) in metadata.items():
            parsed[key] = MetadataValue(item.text, item.value_type)

        return parsed

    def test_file(self, file: CollectedFile):
        """
        Determine whether this is a CHAT file
        """

        return file.filename[-3:].upper() == 'CHA'
