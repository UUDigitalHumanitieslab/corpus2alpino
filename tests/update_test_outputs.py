"""
Script for updating the output files using the current behavior.
"""
import sys
sys.path.append("..")
sys.path.append(".")

from glob import glob
import unittest
import re
from typing import cast, List, Sequence
from os import path

from corpus2alpino.converter import Converter
from corpus2alpino.collectors.filesystem import FilesystemCollector
from corpus2alpino.targets.memory import MemoryTarget
from corpus2alpino.writers.paqu import PaQuWriter

args = sys.argv[1:]
if args:
    patterns = args[0].split(',')
else:
    patterns = ['example*.xml', 'example*.txt', 'example*.cha']

paqu_writer = PaQuWriter()
test_files = cast(List[str], [])
for pattern in patterns:
    test_files += (f for f in glob(path.join(path.dirname(__file__), pattern))
                   if '_expected' not in f)
converter = Converter(
    FilesystemCollector(test_files),
    target=MemoryTarget(),
    writer=paqu_writer)

converted = list(converter.convert())

for test_file, output in zip(test_files, converted):
    expected_filename = re.sub('\.(txt|xml|cha)$', '_expected.txt', test_file)
    with open(expected_filename, mode='w', encoding='utf-8') as expected_file:
        expected_file.write(output)

from test_enrich_lassy import get_enriched

with open('enrichment_expected.xml', mode='w', encoding='utf-8') as expected_file:
    expected_file.write(get_enriched())
