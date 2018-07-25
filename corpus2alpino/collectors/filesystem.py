#!/usr/bin/env python3
from typing import Iterable
from pathlib import Path
from os import path

from corpus2alpino.abstracts import Collector
from corpus2alpino.models import CollectedFile


class FilesystemCollector(Collector):
    def __init__(self, filepaths):
        self.common = path.commonpath(filepaths)
        self.filepaths = filepaths

    def read(self) -> Iterable[CollectedFile]:
        for filepath in self.filepaths:
            (relpath, filename) = path.split(path.relpath(filepath))
            # TODO: mime type?
            yield CollectedFile(relpath, filename, '', open(filepath).read())
