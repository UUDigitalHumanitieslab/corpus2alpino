from corpus2alpino.abstracts import Target
from corpus2alpino.models import Document

from os import path, makedirs
from pathlib import Path


class FilesystemTarget(Target):
    """
    Output chunks to a file using newline separators.
    """

    __current_output_path = None

    def __open_file(self, document, filename, suffix):
        if not self.merge_files:
            output_path = path.join(self.output_path,
                                    document.collected_file.relpath,
                                    document.collected_file.filename)
            if filename != None:
                output_path = path.join(output_path, filename)
            if suffix != None:
                output_path = Path(output_path).with_suffix(suffix)

            if self.__current_output_path != output_path:
                if self.file:
                    self.file.close()
                self.__current_output_path = output_path
                directory = path.split(output_path)[0]
                makedirs(directory, exist_ok=True)
                self.file = open(output_path, 'w', encoding='utf-8')

    def __init__(self, output_path, merge_files=False):
        self.output_path = output_path
        self.index = 1
        self.merge_files = merge_files

        if self.merge_files:
            # using a single file
            self.file = open(output_path, 'w', encoding='utf-8')
        else:
            self.file = None

    def write(self,
              document: Document,
              content: str,
              filename: str = None,
              suffix: str = None):
        self.__open_file(document, filename, suffix)
        self.file.write(content)

    def flush(self):
        return

    def close(self):
        """
        Release resources.
        """
        if self.file:
            self.file.close()
