"""
Script for updating the output files using the current behavior.
"""
import sys
sys.path.append("..")
sys.path.append(".")

import glob
import unittest
from typing import Sequence
from os import path

from corpus2alpino.converter import Converter
from corpus2alpino.collectors.filesystem import FilesystemCollector
from corpus2alpino.targets.memory import MemoryTarget
from corpus2alpino.writers.paqu import PaQuWriter

args = sys.argv[1:]
if args:
    pattern = args[0]
else:
    pattern = '*.xml'

paqu_writer = PaQuWriter()
test_files = glob.glob(path.join(path.dirname(__file__), pattern))
converter = Converter(
    FilesystemCollector(test_files),
    target=MemoryTarget(),
    writer=paqu_writer)

converted = list(converter.convert())

for test_file, output in zip(test_files, converted):
    expected_filename = test_file.replace('.xml', '_expected.txt')
    with open(expected_filename, mode='w') as expected_file:
        expected_file.write(output)
