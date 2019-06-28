#!/usr/bin/env python3
"""
Writes utterances and metadata in PaQu format.
"""

from typing import Iterable

from corpus2alpino.abstracts import Writer, Target
from corpus2alpino.models import Document, MetadataValue, Utterance

FILE_SUFFIX = '.txt'


class PaQuWriter(Writer):
    """
    Wrapper for writing the strings and metadata in PaQu Metadata format
    """

    def write(self, document: Document, target: Target):
        has_metadata = False
        for line in self.output_metadata_items(document.metadata):
            target.write(document, line + '\n', suffix=FILE_SUFFIX)
            has_metadata = True

        if has_metadata:
            target.write(document, '\n', suffix=FILE_SUFFIX)

        for line in self.output_utterances(document.utterances, document.metadata):
            target.write(document, line, suffix=FILE_SUFFIX)

    def output_utterances(self, utterances: Iterable[Utterance], doc_metadata):
        """
        Passthrough input.
        """

        prev_metadata = {**doc_metadata}

        for utterance in utterances:
            # Metadata of an utterance is only derived from the document
            # itself. When read, it is done sequentially (based on
            # previous utterances). If an utterance "reverts" to the
            # meta data value of a document, this must be reset in the
            # output.
            metadata = {}

            # Reset everything
            for key in prev_metadata:
                if not key in utterance.metadata:
                    metadata[key] = MetadataValue('')

            metadata = {**metadata, **doc_metadata, **utterance.metadata}
            metadata_display = '\n'.join(self.output_metadata_items(
                metadata, prev_metadata)) + '\n' if metadata else ''
            yield '{0}{1}|{2}\n\n'.format(metadata_display, utterance.id, utterance.text)
            prev_metadata = {**prev_metadata, **metadata}

    def output_metadata_items(self, metadata, prev_metadata=None):
        for key, item in sorted(metadata.items()):
            if prev_metadata == None or not key in prev_metadata or \
                    prev_metadata[key].value != item.value:
                yield '##META {0} {1} = {2}'.format(item.type, key, item.value)
