#!/usr/bin/env python3
from corpus2alpino.abstracts import Target
from corpus2alpino.models import Document

from os import path, makedirs
from pathlib import Path
from typing import cast, Any


class FilesystemTarget(Target):
    """
    Output chunks to a file using newline separators.
    """

    __current_output_path = None

    def __open_file(self, document: Document, filename: str = None, suffix: str = None):
        if not self.merge_files:
            output_path = path.join(self.output_path,
                                    document.collected_file.relpath,
                                    document.collected_file.filename)

            if document.subpath:
                output_path = path.join(output_path, document.subpath)

            if filename != None:
                output_path = path.join(output_path, cast(str, filename))
            if suffix != None:
                output_path = str(
                    Path(output_path).with_suffix(cast(str, suffix)))

            if self.__current_output_path != output_path:
                if self.file:  # type: ignore
                    self.file.close()  # type: ignore
                self.__current_output_path = output_path  # type: ignore
                directory = path.split(output_path)[0]
                makedirs(directory, exist_ok=True)
                self.file = open(output_path, 'w', encoding='utf-8')

    def __init__(self, output_path: str, merge_files=False) -> None:
        self.output_path = output_path
        self.index = 1
        self.merge_files = merge_files
        if self.merge_files:
            # using a single file
            self.file = open(output_path, 'w', encoding='utf-8')
        else:
            self.file = None  # type: ignore

    def write(self,
              document: Document,
              content: str,
              filename: str = None,
              suffix: str = None):
        self.__open_file(document, filename, suffix)
        if self.file:
            self.file.write(content)

    def flush(self):
        return

    def close(self):
        """
        Release resources.
        """
        if self.file:
            self.file.close()
