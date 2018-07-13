#!/usr/bin/env python3
"""
Wrapper for the Alpino parser.
"""

from xml.sax.saxutils import escape
import socket
import re


class PaQuWriter:
    """
    Wrapper for writing the strings and metadata in PaQu Metadata format
    """

    def parse_lines(self, lines):
        """
        Passthrough input.
        """

        prev_doc_metadata = None
        prev_metadata = {}

        for line, line_id, doc_metadata, sentence_metadata in lines:
            if prev_doc_metadata != doc_metadata:
                yield '\n'.join(self.output_metadata_items(doc_metadata)) + '\n' if doc_metadata else ''
                prev_doc_metadata = doc_metadata
                prev_metadata = {** doc_metadata}

            metadata_display = '\n'.join(self.output_metadata_items(
                sentence_metadata, prev_metadata)) + '\n' if sentence_metadata else ''
            yield f'{metadata_display}{line_id}|{line}\n'

    def output_metadata_items(self, metadata, prev_metadata=None):
        for key, value in metadata.items():
            if prev_metadata == None or not key in prev_metadata or \
                    prev_metadata[key] != value:
                yield f'##META text {key} = {value}'

        if prev_metadata != None:
            prev_metadata.clear()
            prev_metadata.update(metadata)
