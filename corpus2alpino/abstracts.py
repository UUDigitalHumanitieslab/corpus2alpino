#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import Iterable
from os import path
from pathlib import Path

from corpus2alpino.models import CollectedFile, Document


class Collector(ABC):
    """
    Collects files from some data source.
    """

    @abstractmethod
    def read(self) -> Iterable[CollectedFile]:
        pass


class Reader(ABC):
    @abstractmethod
    def read(self, file: CollectedFile) -> Iterable[Document]:
        """
        Reads a file and returns the documents found in the file and its
        utterances.
        """

        pass

    @abstractmethod
    def test_file(self, file: CollectedFile) -> bool:
        """
        Tests whether a file can be read by this reader.
        """

        pass


class Annotator(ABC):
    @abstractmethod
    def annotate(self, document: Document) -> None:
        """
        Adds annotations to a document and utterances. For example
        a syntactic parse.
        """

        pass


class Target(ABC):
    """
    Wraps a file target, this can be a file system, a zip-file, 
    a database, etc, any place where files could be written to.
    """

    def target_path(self, document: Document,
                    filename: str,
                    suffix: str) -> str:
        output_path = path.join(document.collected_file.relpath,
                                document.collected_file.filename)
        if filename != None:
            output_path = path.join(output_path, filename)
        if suffix != None:
            output_path = Path(output_path).with_suffix(suffix)
        return output_path

    @abstractmethod
    def write(self,
              document: Document,
              content: str,
              filename: str = None,
              suffix: str = None):
        pass


class Writer(ABC):
    """
    Writes documents as files in a desired format to a target.
    """

    @abstractmethod
    def write(self, document: Document, target: Target):
        pass
