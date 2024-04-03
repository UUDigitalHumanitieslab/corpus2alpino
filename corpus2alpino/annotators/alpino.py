#!/usr/bin/env python3
"""
Wrapper for the Alpino parser.
"""

from .alpino_client import AlpinoProcessClient, AlpinoServerClient
from corpus2alpino.models import Document, MetadataValue
from corpus2alpino.abstracts import Annotator
import re
import os
import logging

from typing import cast, Union, List

ANNOTATION_KEY = 'alpino'


timealign_symbol = re.compile(r'\u0015')


class AlpinoAnnotator(Annotator):

    """
    Wrapper for annotating using Alpino (server or local).
    """

    def __init__(self, host_or_path: str, port_or_args: Union[int, List[str]]):
        self.client = self.get_client(host_or_path, port_or_args)

    def get_client(self, host_or_path: str, port_or_args: Union[int, List[str]]) -> Union[AlpinoProcessClient, AlpinoServerClient]:
        if os.path.isfile(host_or_path) or os.path.isdir(host_or_path):
            return AlpinoProcessClient(
                host_or_path, cast(List[str], port_or_args))
        else:
            return AlpinoServerClient(
                host_or_path, cast(int, port_or_args))

    def annotate(self, document: Document):
        for utterance in document.utterances:
            try:
                if not ANNOTATION_KEY in utterance.annotations:
                    # replace the symbol with a middot to prevent XML parsing errors
                    utterance.annotations[ANNOTATION_KEY] = timealign_symbol.sub(
                        "·",
                        self.client.parse_line(utterance.text, utterance.id))
                    if self.client.version:
                        utterance.metadata['alpino_version'] = MetadataValue(
                            self.client.version)
                    if self.client.version_date:
                        utterance.metadata['alpino_version_date'] = MetadataValue(
                            self.client.version_date.isoformat(), 'date')
            except Exception as exception:
                logging.getLogger().error(
                    Exception("Problem parsing: {0}:{1}|{2}\n{3}".format(self.__document_path(document), utterance.id, utterance.text, exception)))

    def __document_path(self, document: Document):
        value = document.collected_file.filename

        if document.collected_file.relpath:
            value = document.collected_file.relpath + '/' + value

        if document.subpath:
            value += '//' + document.subpath

        return value
