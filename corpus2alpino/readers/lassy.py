#!/usr/bin/env python3
"""
Module for reading Lassy/Alpino xml files.
"""

from typing import Iterable
from lxml import etree

from .alpino_brackets import escape_id, escape_word, format_add_lex, format_folia
from corpus2alpino.abstracts import Reader
from corpus2alpino.annotators.alpino import ANNOTATION_KEY
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance


class LassyReader(Reader):
    """
    Class for converting Lassy/Alpino xml (treebank) files to documents.
    """

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        try:
            if '<treebank' in collected_file.content[0:400]:
                treebank = etree.fromstring(collected_file.content)
                yield Document(
                    collected_file,
                    [self.get_utterance(tree) for tree in treebank.iter("alpino_ds")])
            else:
                tree = etree.fromstring(collected_file.content)
                yield Document(
                    collected_file,
                    [self.get_utterance(tree)])
        except Exception as e:
            raise Exception(collected_file.relpath + "/" +
                            collected_file.filename) from e

    def get_utterance(self, tree) -> Utterance:
        """
        Read Alpino lxml Element and returns an Utterance object.
        """
        sentence = tree.find("sentence")
        utterance = Utterance(
            sentence.text,
            sentence.attrib['sentid'],
            self.get_metadata(tree),
            int(sentence.attrib['sentid'], 10))
        metadata_element = tree.find("metadata")
        if metadata_element is not None:
            # remove metadata element from output,
            # this metadata is now in the Utterance
            tree.remove(metadata_element)
        xml = etree.tostring(tree, encoding='utf8').decode('utf8')
        utterance.annotations[ANNOTATION_KEY] = xml.strip()
        return utterance

    def get_metadata(self, tree):
        metadata = {}
        for meta in tree.findall("./metadata/meta"):
            metadata[meta.attrib['name']] = MetadataValue(
                meta.attrib['value'], meta.attrib['type'])

        return metadata

    def test_file(self, file: CollectedFile):
        """
        Determine whether this is an Alpino/Lassy XML file
        """

        return '<alpino_ds' in file.content[0:400]
