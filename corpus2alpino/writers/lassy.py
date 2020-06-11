#!/usr/bin/env python3
from typing import Dict

import re
import logging
from xml.sax.saxutils import escape

from corpus2alpino.annotators.alpino import ANNOTATION_KEY
from corpus2alpino.abstracts import Writer, Target
from corpus2alpino.models import Document, MetadataValue, Utterance


class LassyWriter(Writer):
    def __init__(self, merge_treebanks: bool) -> None:
        self.merge_treebanks = merge_treebanks

    def write(self, document: Document, target: Target):
        if self.merge_treebanks:
            target.write(
                document,
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<treebank>")

            for utterance in document.utterances:
                self.write_utterance(document, target, utterance)

            target.write(document, '</treebank>')
        else:
            index = 1

            for utterance in document.utterances:
                self.write_utterance(document, target, utterance,
                                     '{0}.xml'.format(index))
                index += 1

    def write_utterance(self, document: Document, target: Target, utterance: Utterance, filename=None):
        try:
            annotation = utterance.annotations[ANNOTATION_KEY]
        except KeyError:
            logging.getLogger().warning(
                'Annotation missing for: {0}|{1} ({2})'.format(utterance.id, utterance.text, document.subpath))
            return

        target.write(document, self.render_annotation(
            document, utterance, not filename), filename)

    def render_annotation(self, document: Document, utterance: Utterance, remove_header=False) -> str:
        metadata = {**document.metadata, **utterance.metadata}
        annotation = utterance.annotations[ANNOTATION_KEY]

        if not metadata and remove_header == False:
            return annotation

        lines = annotation.splitlines()

        if remove_header:
            # remove the xml header and remove the trailing newline
            if '<?xml' in lines[0]:
                lines = lines[1:]
            lines[-1] = lines[-1].rstrip()

        existing_metadata = -1

        if metadata:
            for i in range(0, len(lines)):
                line = lines[i]
                if '<metadata' in line:
                    existing_metadata = i
                elif existing_metadata >= 0:
                    meta_name_search = re.search(
                        '<meta .*name="([^"]+)".*?/>', line)
                    if meta_name_search:
                        name = meta_name_search.group(1)
                        try:
                            item = metadata[name]
                            lines[i] = self.render_metadata_value(name, item)
                            del metadata[name]
                        except KeyError:
                            pass
                    elif '</metadata>' in line:
                        existing_metadata = i
                        break

        if metadata:
            lines.insert(existing_metadata, self.render_metadata(
                metadata, existing_metadata == -1))

        return "\n".join(lines)

    def render_metadata(self, metadata: Dict[str, MetadataValue], wrap: bool) -> str:
        return ("<metadata>\n" if wrap else "") + "\n".join(
            self.render_metadata_value(key, item) for (key, item) in metadata.items()
        ) + ("\n</metadata>" if wrap else "")

    def render_metadata_value(self, key: str, item: MetadataValue) -> str:
        return '<meta type="{0}" name="{1}" value="{2}" />'.format(item.type, key, self.escape_xml_attribute(item.value))

    def escape_xml_attribute(self, value: str) -> str:
        escaped = escape(value).replace('\n', '&#10;').replace(
            '\r', '').replace('"', '&quot;')
        # replace CHAT time alignment character with middot because it borks lxml
        return escaped.replace('\x15', '&#183;')
