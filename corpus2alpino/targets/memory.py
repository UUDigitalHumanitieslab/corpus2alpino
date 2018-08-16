from os import path
from pathlib import Path

from corpus2alpino.abstracts import Target
from corpus2alpino.models import Document


class MemoryTarget(Target):
    """
    Combine output in memory.
    """
    buffer = ''

    def write(self,
              document: Document,
              content: str,
              filename: str = None,
              suffix: str = None):
        """
        Write all lines to stdout.
        """
        self.buffer += content

    def flush(self):
        try:
            return self.buffer
        finally:
            self.buffer = ''

    def close(self):
        return
