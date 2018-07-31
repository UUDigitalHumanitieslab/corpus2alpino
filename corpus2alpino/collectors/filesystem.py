#!/usr/bin/env python3
import glob
from typing import Iterable, List
from pathlib import Path
from os import path

from corpus2alpino.abstracts import Collector
from corpus2alpino.models import CollectedFile


class FilesystemCollector(Collector):
    position = 0

    def __init__(self, filepaths: List[str]) -> None:
        self.common = path.commonpath(filepaths)
        self.filepaths = filepaths
        self.total = len(filepaths)

    def read(self) -> Iterable[CollectedFile]:
        self.position = 0
        for filepath in self.filepaths:
            globbed = glob.glob(filepath, recursive=True)
            self.total += len(globbed) - 1

            for match in globbed:
                (relpath, filename) = path.split(path.relpath(match, self.common))
                # TODO: mime type?
                with open(match) as file:
                    yield CollectedFile(relpath, filename, '', file.read())
                self.position += 1
