"""
Unit test for corpus to Alpino converter.
"""

import glob
import unittest
from typing import Sequence
from os import path

from corpus2alpino.annotators.alpino import ANNOTATION_KEY
from corpus2alpino.annotators.enrich_lassy import EnrichLassyAnnotator
from corpus2alpino.models import Utterance


class TestEnrichLassy(unittest.TestCase):
    """
    Unit test class.
    """

    def setUp(self):
        self.maxDiff = None

    def test_enrich(self):
        """
        Test that sentences in a CHAT/FoLiA/TEI file can be converted to Alpino-compatible input.
        """
        with open(get_filepath("enrichment_expected.xml")) as expected:
            self.assertEqual(get_enriched(), expected.read())


def get_enriched():
    enricher = EnrichLassyAnnotator(get_filepath("enrichment.csv"))
    with open(get_filepath("example_lassy.xml")) as lassy:
        utterance = Utterance(
            "dit is een test",
            "1",
            {},
            0,
            {
                ANNOTATION_KEY: lassy.read()
            })
    enricher.enrich_utterance(utterance)

    return utterance.annotations[ANNOTATION_KEY]


def get_filepath(filename: str) -> str:
    return path.join(path.dirname(__file__), filename)
