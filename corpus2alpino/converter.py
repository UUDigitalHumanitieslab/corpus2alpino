#!/usr/bin/env python3
from typing import List, Optional

from corpus2alpino.readers.auto import AutoReader
from corpus2alpino.targets.console import ConsoleTarget
from corpus2alpino.writers.paqu import PaQuWriter

from corpus2alpino.abstracts import Annotator, Collector, Reader, Target, Writer


class Converter:
    """
    Class for converting files to Alpino XML (input) files.
    """

    def __init__(
        self,
        collector: Collector,
        annotators: Optional[List[Annotator]] = None,
        reader: Reader = AutoReader(),
        writer: Writer = PaQuWriter(),
        target: Target = ConsoleTarget(),
    ) -> None:
        self.collector = collector
        self.annotators = annotators or []
        self.reader = reader
        self.writer = writer
        self.target = target

    def convert(self):
        for file in self.collector.read():
            for document in self.reader.read(file):
                for annotator in self.annotators:
                    annotator.annotate(document)
                self.writer.write(document, self.target)
                yield self.target.flush()
        self.target.close()
