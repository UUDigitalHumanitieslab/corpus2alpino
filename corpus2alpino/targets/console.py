from os import path
from pathlib import Path

from corpus2alpino.abstracts import Target
from corpus2alpino.models import Document


class ConsoleTarget(Target):
    """
    Output chunks to the console on separate lines.
    """

    def write(self,
              document: Document,
              content: str,
              filename: str = None,
              suffix: str = None):
        """
        Write all lines to stdout.
        """
        print(content, end='')

    def flush(self):
        return

    def close(self):
        return
