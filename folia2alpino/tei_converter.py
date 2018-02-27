"""
Module for converting TEI xml files to Alpino XML (input) files.
"""
from tei_reader import TeiReader
import ucto


class TeiConverter:
    """
    Class for converting a TEI xml files to Alpino XML (input) files.

    Arguments:
        wrapper --- Wrapper for communicating with the Alpino parser.
    """

    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.reader = TeiReader()
        self.tokenizer = ucto.Tokenizer("tokconfig-nld")

    def get_parses(self, file_names):
        """
        Get the parses and a wrapping treebank xml structure.
        """

        sentences = self.get_sentences(file_names)
        return self.wrapper.parse_lines(sentences)

    def get_sentences(self, file_names):
        """
        Read TEI files and return Alpino parsable sentences.
        """

        for file_name in file_names:
            corpora = self.reader.read_file(file_name)

            for document in corpora.documents:
                unique_ids = {}  # an id should be unique within a document
                for division_path in self.get_lowest_divisions(document.divisions):
                    self.tokenizer.process(division_path[-1].text)
                    for sentence in self.tokenizer.sentences():
                        # TODO: support quoted text
                        # TODO: support some more word-specific annotations (@mwu, @skip, @phantom, @folia, @id ...)
                        # Maybe try to align the tokenized sentences with the text parts and their attributes?
                        metadata = self.get_metadata(document, division_path)
                        sentence_id = self.determine_id(
                            sentence, file_name, metadata, unique_ids)
                        yield (sentence, sentence_id, metadata)

    def determine_id(self, sentence, file_name, metadata, unique_ids):
        if 'id' in metadata:
            sentence_id = self.escape_id(metadata['id'])
        else:
            sentence_id = file_name

        if sentence_id in unique_ids:
            unique_ids[sentence_id] += 1
            return f"{sentence_id}_{unique_ids[sentence_id]}"
        else:
            unique_ids[sentence_id] = 0
            return sentence_id

    def get_lowest_divisions(self, divisions, path=[]):
        for division in divisions:
            empty = True
            for sub_division in self.get_lowest_divisions(division.divisions, path + [division]):
                empty = False
                yield sub_division
            if empty:
                # has no child
                yield path + [division]

    def get_metadata(self, document, division_path):
        metadata = self.get_element_metadata(document.attributes)
        for division in division_path:
            metadata = {
                **metadata,
                **self.get_element_metadata(division.attributes)
            }

        return metadata

    def get_element_metadata(self, attributes):
        metadata = {}
        for attribute in attributes:
            if attribute.key in metadata:
                metadata[attribute.key] += ' | ' + attribute.text
            else:
                metadata[attribute.key] = attribute.text
        return metadata

    def escape_id(self, sentence_id):
        """
        Escape an id to be Alpino compatible.
        """

        return self.escape_word(sentence_id.replace("|", "_"))

    def escape_word(self, text):
        """
        Escape a word to be Alpino compatible.
        """

        return text.replace("[", "\\[").replace("]", "\\]")

    def test_file(self, file_name):
        """
        Determine whether this is a TEI XML file
        """

        with open(file_name) as file:
            for i in range(0, 5):
                line = file.readline()
                if not line:
                    return False
                if '<TEI' in line:
                    return True

        return False
