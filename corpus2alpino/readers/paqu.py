#!/usr/bin/env python3
"""
Module for reading (PaQu metadata) plain text files to parsable utterances.
"""
from typing import Dict, Iterable, List, Tuple

import os
import re
import ucto

from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance

metadata_pattern = re.compile(r'^##META ([^\s]+) ([^\s]+) ?= ?(.*)$')
id_pattern = re.compile(r'([^\s]+)\|(.*)$')
int_pattern = re.compile('^\d+$')


class PaQuReader(Reader):
    """
    Class for converting a PaQu metadata or plain text file to documents.
    """

    def __init__(self, tokenizer=None) ->None:
        self.tokenizer = tokenizer if tokenizer else ucto.Tokenizer(
            "tokconfig-nld")

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        file_metadata = None
        metadata = {} # type: ignore
        # files can start with its own metadata
        reading_file_metadata = True
        text_lines = [] # type: ignore

        for line in collected_file.content.splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                # blank line
                if metadata:
                    if reading_file_metadata:
                        file_metadata = metadata
                        metadata = {}
                reading_file_metadata = False
                continue

            # a non empty line should either contain metadata or text
            metadata_match = metadata_pattern.match(stripped_line)
            if metadata_match:
                # metadata after reading lines? new document!
                if text_lines:
                    yield Document(
                        collected_file,
                        self.parse_utterances(metadata, text_lines),
                        {**(file_metadata or {}), **(metadata or {})},
                        self.get_subpath(metadata))
                    metadata = {}
                    text_lines = []
                (type, var, value) = metadata_match.groups()
                metadata[var] = MetadataValue(value, type)
            else:
                id_match = id_pattern.match(stripped_line)
                if id_match:
                    # id for utterance
                    (id, text) = id_match.groups()
                else:
                    id = None # type: ignore
                    text = stripped_line
                text_lines += [(id, text)]

        if text_lines:
            yield Document(collected_file,
                           self.parse_utterances(metadata, text_lines),
                           {**(file_metadata or {}), **(metadata or {})},
                           self.get_subpath(metadata))

    def parse_utterances(self, metadata: Dict[str, MetadataValue], text_lines: List[Tuple[str, str]]):
        for i in range(0, len(text_lines)):
            (id, text) = text_lines[i]
            if id == None:
                try:
                    id = metadata["uttid"].value
                except KeyError:
                    id = str(i)
            self.tokenizer.process(text)
            j = 0
            for sentence in self.tokenizer.sentences():
                yield Utterance(sentence,
                                '{0}-{1}'.format(id, j),
                                metadata,
                                i)
                j += 1

    def test_file(self, file: CollectedFile):
        """
        Determine whether this is a TXT file
        """

        return file.filename[-3:].upper() == 'TXT'

    def get_subpath(self, metadata: Dict[str, MetadataValue]) -> str:
        for key in ['id', 'messageid']:
            try:
                return metadata[key].value
            except KeyError:
                pass
        return ''
        