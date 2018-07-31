#!/usr/bin/env python3
from typing import Dict, List


class CollectedFile:
    def __init__(self, relpath: str, filename: str, mimetype: str,
                 content: str) -> None:
        self.relpath = relpath
        self.filename = filename
        self.mimetype = mimetype
        self.content = content


class MetadataValue:
    def __init__(self, value: str, type: str='text') -> None:
        self.value = value
        self.type = type


class Utterance:
    def __init__(self,
                 text: str,
                 id: str,
                 metadata: Dict[str, MetadataValue] = {},
                 line: int = 0,
                 annotations: dict = {}) -> None:
        self.text = text
        self.id = id
        self.metadata = metadata
        self.line = line
        self.annotations = annotations


class Document:
    annotations: dict = {}

    def __init__(self,
                 collected_file: CollectedFile,
                 utterances: List[Utterance],
                 metadata: Dict[str, MetadataValue] = {},
                 subpath: str = '') -> None:
        """
        A document found in a file.

        subpath: if a file has an internal structure, this
            contains a string representation of that relative to
            the file. E.g. if a tei.xml contains a document A at the
            root and a document B 

        """
        self.collected_file = collected_file
        self.utterances = utterances
        self.subpath = subpath
        self.metadata = metadata
