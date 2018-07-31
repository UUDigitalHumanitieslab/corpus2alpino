#!/usr/bin/env python3
"""
Module for reading TEI xml files to document, utterances and metadata.
"""
from typing import Dict, Iterable, List, Tuple
from tei_reader import TeiReader as TeiParser
from tei_reader.models.part import Part
import os
import re
import ucto

from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance

from corpus2alpino.readers.alpino_brackets import escape_id, format_folia

alignable_characters = re.compile(r'[A-Za-zàéëüïóò]')
nonalignable_characters = re.compile(r'[^A-Za-zàéëüïóò]')

ucto_ligatures = {
    'æ': "ae",
    'Æ': "AE",
    'œ': "oe",
    'Œ': "OE",
    'ĳ': "ij",
    'Ĳ': "IJ",
    'ﬂ': "fl",
    'ﬀ': "ff",
    'ﬃ': "ffi",
    'ﬄ': "ffl",
    'ﬅ': "st",
    'ß': "ss"
}


class TokenizedSentenceEmitter:
    offset = 0

    def __init__(self, sentences: List[str]) -> None:
        self.sentences = sentences

    def __get_alignable_text(self, text: str) -> str:
        return nonalignable_characters.sub('', ''.join([ucto_ligatures[c] if c in ucto_ligatures else c for c in text]))

    def get_sentences(self, part_text: str, part_offset: int=0) -> Iterable[str]:
        if not self.sentences:
            return
        sentence = self.sentences[0] + '\n'

        remaining_sentence = sentence[self.offset:]

        alignable_text = self.__get_alignable_text(part_text)

        (sentence_length, part_offset, part_done) = self.get_part_length(
            remaining_sentence, alignable_text, part_offset)
        yield remaining_sentence[:sentence_length]
        if part_done:
            self.offset += sentence_length
        else:
            self.offset = 0
            # move to next sentence
            self.sentences = self.sentences[1:]
            yield from self.get_sentences(part_text, part_offset)

    def get_part_length(self, sentence: str, alignable_text: str, n: int=0) -> Tuple[int, int, bool]:
        """
        Return the actual string length of this part in the sentence and the index of the alignable character match
        in this part. This index is relevant if a part is split over multiple sentences
        """

        for i, char in enumerate(sentence):
            if alignable_characters.match(char):
                if len(alignable_text) == n:
                    # part of the sentence matches
                    return (i, n, True)
                if alignable_text[n] != char:
                    # this part doesn't match
                    raise Exception(
                        f"Alignment error at ({i}, {n})! Sentence: {sentence} Part: {alignable_text}")
                n += 1

        # the entire sentence matches
        return (len(sentence), n, False)


class TeiReader(Reader):
    """
    Class for converting a TEI xml file to documents.
    """

    def __init__(self) ->None:
        self.reader = TeiParser()
        self.tokenizer = ucto.Tokenizer("tokconfig-nld")

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        corpora = self.reader.read_string(collected_file.content)

        for document in corpora.documents:
            # an id should be unique within a document
            unique_ids: Dict[str, str] = {}
            doc_metadata: Dict[str, MetadataValue] = {}
            utterances: List[Utterance] = []
            for division_path in self.get_lowest_divisions(document.divisions):
                division = division_path[-1]
                self.tokenizer.process(division.text)
                sentence_emitter = TokenizedSentenceEmitter(
                    list(self.tokenizer.sentences()))

                for sentence in division.tostring(
                        lambda part,
                        text: self.add_word_metadata(sentence_emitter,
                                                     part,
                                                     text)).splitlines():
                    (doc_metadata, sentence_metadata) = self.get_metadata(
                        document, division_path)
                    # TODO: id from part if there is only one part?
                    sentence_id = self.determine_id(
                        collected_file.filename,
                        doc_metadata,
                        sentence_metadata,
                        unique_ids)

                    utterances.append(
                        Utterance(sentence, sentence_id, sentence_metadata))

            # TODO: get document id/path?
            yield Document(collected_file, utterances, doc_metadata)

    def modify_text(self, text, modification):
        """
        Only modify the first line.
        """

        lines = text.splitlines()
        if len(lines) > 1:
            # if a text has newlines, end the quotation
            return (modification(lines[0].replace('\n', '')) + '\n' + ''.join(lines[1:])).replace('  ', ' ')
        else:
            return modification(text)

    def determine_id(self, file_name, doc_metadata, sentence_metadata, unique_ids):
        if 'id' in doc_metadata:
            sentence_id = escape_id(doc_metadata['id'].value)
        elif 'id' in sentence_metadata:
            sentence_id = escape_id(sentence_metadata['id'].value)
        else:
            _, sentence_id = os.path.split(file_name)

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

    def get_metadata(self, document, division_path) -> \
            Tuple[Dict[str, MetadataValue], Dict[str, MetadataValue]]:
        doc_metadata = self.get_element_metadata(document.attributes)
        sentence_metadata: Dict[str, MetadataValue] = {}
        for division in division_path:
            sentence_metadata = {
                **sentence_metadata,
                **self.get_element_metadata(division.attributes)
            }

        return (doc_metadata, sentence_metadata)

    def get_element_metadata(self, attributes) -> Dict[str, MetadataValue]:
        metadata: Dict[str, MetadataValue] = {}
        for attribute in attributes:
            if attribute.key in metadata:
                metadata[attribute.key].value += ' | ' + attribute.text
            else:
                metadata[attribute.key] = MetadataValue(attribute.text)
        return metadata

    def test_file(self, file):
        """
        Determine whether this is a TEI XML file
        """

        return '<TEI' in file.content[0:100]

    def add_word_metadata(self, sentence_emitter: TokenizedSentenceEmitter, part: Part, text: str):
        if len(list(part.parts)) == 0:
            text = ''.join(sentence_emitter.get_sentences(part.text))

        attributes = self.get_element_metadata(part.attributes)

        if 'tei-tag' in attributes:
            tag = attributes['tei-tag'].value
            if tag == 'q':
                return self.modify_text(text, lambda text: f'" {text}"')

        if 'id' in attributes:
            identifier = attributes['id'].value
            # TODO: I think this is a bug in Alpino? "ERROR: something went wrong in saving the XML in stream($stream(140026222726096))!"
            # return self.modify_text(text, lambda text: f'[ @id {identifier} ] {text}')

        if 'lemma' in attributes and 'pos' in attributes:
            lemma = attributes['lemma'].value
            pos_tag = attributes['pos'].value
            return self.modify_text(text, lambda text: format_folia(lemma, pos_tag, text.strip()) + ' ')

        return text
