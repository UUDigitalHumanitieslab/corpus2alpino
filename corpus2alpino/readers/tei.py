#!/usr/bin/env python3
"""
Module for reading TEI xml files to document, utterances and metadata.
"""
from typing import Dict, Iterable, List, Tuple
from tei_reader import TeiReader as TeiParser
from tei_reader.models.part import Part
from tei_reader.models.placeholder_division import PlaceholderDivision

import os
import re
import ucto

from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance

from corpus2alpino.readers.alpino_brackets import escape_id, format_folia

alignable_characters = re.compile(r'[A-Za-zàéëüïóò,\.:;0123456789]')
nonalignable_characters = re.compile(r'[^A-Za-zàéëüïóò,\.:;0123456789]')

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
                        "Alignment error at ({0}, {1})! Sentence: {2} Part: {3}".format(i, n, sentence, alignable_text))
                n += 1

        # the entire sentence matches
        return (len(sentence), n, False)


class TeiReader(Reader):
    """
    Class for converting a TEI xml file to documents.
    """

    def __init__(self, tokenizer=None) ->None:
        self.reader = TeiParser()
        self.tokenizer = tokenizer if tokenizer else ucto.Tokenizer(
            "tokconfig-nld")

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        corpora = self.reader.read_string(collected_file.content)

        for document in corpora.documents:
            # an id should be unique within a document
            unique_ids = {} # type: ignore
            doc_metadata = self.get_element_metadata(document.attributes)
            utterances = []
            for (division_path, div_metadata) in self.get_lowest_divisions(
                    document.divisions):
                division = division_path[-1]

                self.tokenizer.process(division.text)
                sentence_emitter = TokenizedSentenceEmitter(
                    list(self.tokenizer.sentences()))

                # aggregate all the metadata of the sentence parts
                annotated_sentences = [('', {})] # type: ignore

                for (text, metadata, newline) in self.annotate_parts(
                        division.parts, sentence_emitter):
                    (current_text, current_metadata) = annotated_sentences[-1]
                    annotated_sentences[-1] = (
                        current_text + text,
                        self.merge_metadata_sibbling(current_metadata, metadata))
                    if newline:
                        annotated_sentences.append(('', {}))

                for [sentence, sentence_metadata] in annotated_sentences:
                    if not sentence:
                        # empty sentence
                        continue

                    # assume the metadata of the divider is more relevant
                    metadata = self.merge_metadata_child(
                        sentence_metadata, div_metadata)
                    sentence_id = self.determine_id(
                        collected_file.filename,
                        doc_metadata,
                        metadata,
                        unique_ids)

                    utterances.append(
                        Utterance(sentence.replace('  ', ' '), sentence_id, metadata))
            # TODO: get document id/path?
            yield Document(collected_file, utterances, doc_metadata)

    def determine_id(self, file_name, doc_metadata, sentence_metadata, unique_ids: Dict[str, int]):
        if 'id' in doc_metadata:
            sentence_id = escape_id(doc_metadata['id'].value)
        elif 'id' in sentence_metadata:
            sentence_id = escape_id(sentence_metadata['id'].value)
        else:
            _, sentence_id = os.path.split(file_name)

        if sentence_id in unique_ids:
            unique_ids[sentence_id] += 1
            return "{0}_{1}".format(sentence_id, unique_ids[sentence_id])
        else:
            unique_ids[sentence_id] = 0
            return sentence_id

    def get_lowest_divisions(self, divisions, path=[]):
        for division in divisions:
            empty = True
            metadata = self.get_element_metadata(division.attributes)
            for (sub_division_path, submetadata) in self.get_lowest_divisions(
                    division.divisions, path + [division]):
                empty = False
                yield (sub_division_path, {**metadata, **submetadata})
            if empty:
                # has no child
                yield (path + [division], metadata)

    def get_element_metadata(self, attributes) -> Dict[str, MetadataValue]:
        metadata = {} # type: ignore
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

        return '<TEI' in file.content[0:400]

    def merge_metadata_sibbling(self, prev, current):
        result = {**prev, **current}

        for (key, data) in current.items():
            if key in prev:
                result[key] = MetadataValue(
                    ' | '.join(sorted(set(
                        prev[key].value.split(' | ') +
                        data.value.split(' | ')))))
        return result

    def merge_metadata_child(self, child, parent):
        result = {**parent, **child}

        for (key, value) in parent.items():
            # Parent's property is more important: e.g. the tag of the parent
            # item of a sentence is more relevant for the utterance metadata
            # than that of a single word inside that utterance.
            if key in ['tei-tag', 'id']:
                result[key] = value
        return result

    def annotate_parts(
            self, parts, sentence_emitter: TokenizedSentenceEmitter):
        for part in parts:
            text = ''
            metadata = {} # type: ignore
            empty = True
            part_metadata = self.get_element_metadata(part.attributes)
            for (subpart_text, subpart_metadata, newline) in \
                    self.annotate_parts(part.parts, sentence_emitter):
                empty = False
                text += subpart_text
                metadata = self.merge_metadata_sibbling(
                    metadata, subpart_metadata)

                if newline:
                    yield self.emit_part(text, metadata, part_metadata, True)
                    metadata = {}
                    text = ''

            if empty:
                # has no child
                sentences = list(sentence_emitter.get_sentences(part.text))
                if sentences:
                    for sentence in sentences[:-1]:
                        text += sentence
                        yield self.emit_part(text, metadata, part_metadata, True)
                        text = ''

                    text += self.inline_metadata(
                        sentences[-1], part_metadata)

            if text:
                yield self.emit_part(text,
                                     metadata,
                                     part_metadata,
                                     False)

    def emit_part(self, text: str, subparts_metadata: Dict[str, MetadataValue], part_metadata: Dict[str, MetadataValue], newline):
            # Reverse priority for metadata: the attributes of the
            # highest node in the tree should take precedence.
        return self.inline_metadata(text, part_metadata), \
            self.merge_metadata_child(subparts_metadata, part_metadata), \
            newline

    def inline_metadata(self, text: str, metadata):
        """
        Format applicable metadata using the bracketed input of Alpino
        https://www.let.rug.nl/vannoord/alp/Alpino/AlpinoUserGuide.html
        """

        # remove redundant spaces
        text = text.replace('  ', ' ')

        if 'tei-tag' in metadata:
            tag = metadata['tei-tag'].value
            if tag == 'q':
                return ' " {0} " '.format(text.strip())

        if 'id' in metadata:
            identifier = metadata['id'].value
            # TODO: I think this is a bug in Alpino? "ERROR: something went wrong in saving the XML in stream($stream(140026222726096))!"
            # return f'[ @id {identifier} ] {text}'

        if 'lemma' in metadata and ('pos' in metadata or 'type' in metadata):
            lemma = metadata['lemma'].value
            pos_key = 'pos' if 'pos' in metadata else 'type'
            pos_tag = metadata[pos_key].value

            # This metadata is marked in the utterance now
            del metadata['lemma']
            del metadata[pos_key]

            return format_folia(lemma, pos_tag, text.strip()) + ' '

        return text
