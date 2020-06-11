"""
Unit test for corpus to Alpino converter.
"""

import glob
import unittest
from typing import Sequence
from os import path

from corpus2alpino.converter import Converter
from corpus2alpino.collectors.filesystem import FilesystemCollector
from corpus2alpino.targets.memory import MemoryTarget
from corpus2alpino.writers.paqu import PaQuWriter


class TestCorpus2Alpino(unittest.TestCase):
    """
    Unit test class.
    """
    def setUp(self):
        self.maxDiff = None

    def test_get_sentences(self):
        """
        Test that sentences in a CHAT/FoLiA/TEI file can be converted to Alpino-compatible input.
        """

        paqu_writer = PaQuWriter()
        test_files = self.get_files('example*.xml') + self.get_files('example*.cha')
        converter = Converter(
            FilesystemCollector(test_files),
            target=MemoryTarget(),
            writer=paqu_writer)

        converted = list(converter.convert())
        self.assertEqual(len(converted), len(test_files))

        for test_file, output in zip(test_files, converted):
            print(test_file)
            expected_filename = test_file.replace('.xml', '_expected.txt').replace('.cha', '_expected.txt')
            with open(expected_filename, encoding='utf-8') as expected_file:
                self.assertEqual(
                    output,
                    expected_file.read())

    def get_files(self, pattern):
        return sorted(glob.glob(path.join(path.dirname(__file__), pattern)))
