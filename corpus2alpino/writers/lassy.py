from corpus2alpino.annotators.alpino import ANNOTATION_KEY
from corpus2alpino.abstracts import Writer, Target
from corpus2alpino.models import Document


class LassyWriter(Writer):
    def __init__(self, merge_treebanks: bool) -> None:
        self.merge_treebanks = merge_treebanks

    def write(self, document: Document, target: Target):
        # TODO: give warning if annotation is missing
        if self.merge_treebanks:
            target.write(
                document,
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<treebank>")

            for utterance in document.utterances:
                # remove the xml header and remove the trailing newline
                lines = utterance.annotations[ANNOTATION_KEY].splitlines()
                lines = lines[1:]
                lines[-1] = lines[-1].rstrip()

                for line in lines:
                    target.write(document, line + '\n')

            target.write(document, '</treebank>')
        else:
            index = 1

            for utterance in document.utterances:
                target.write(
                    document, utterance.annotations[ANNOTATION_KEY],
                    f'{index}.xml')
                index += 1
