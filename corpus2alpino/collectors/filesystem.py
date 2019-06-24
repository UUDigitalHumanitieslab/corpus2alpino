#!/usr/bin/env python3
import glob
from typing import Iterable, List
from pathlib import Path
from os import listdir, path

from corpus2alpino.abstracts import Collector
from corpus2alpino.models import CollectedFile


class FilesystemCollector(Collector):
    position = 0

    def __clear_pattern(self, filepath: str) -> str:
        realpath = filepath.split('*')[0]
        if path.isdir(realpath):
            return realpath
        else:
            return path.split(realpath)[0]

    def __init__(self, filepaths: List[str]) -> None:
        # Only determine common directory up to the first pattern
        self.common = path.commonpath(list(
            self.__clear_pattern(filepath) for filepath in filepaths))
        self.filepaths = filepaths
        self.total = len(filepaths)

    def read(self) -> Iterable[CollectedFile]:
        self.position = 0
        return self.yield_files(self.filepaths)

    def yield_files(self, filepaths, encoding: str = 'utf-8'):
        for filepath in filepaths:
            globbed = glob.glob(filepath, recursive=True)
            self.total += len(globbed) - 1

            for match in globbed:
                if path.isdir(match):
                    yield from self.yield_files(
                        path.join(match, file) for file in listdir(match))
                    continue

                (relpath, filename) = path.split(
                    path.relpath(match, self.common))
                # TODO: mime type?
                with open(match, encoding=encoding) as file:
                    yield CollectedFile(relpath, filename, '', file.read())
                self.position += 1
