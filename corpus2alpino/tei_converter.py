#!/usr/bin/env python3
"""
Module for converting TEI xml files to Alpino XML (input) files.
"""
from tei_reader import TeiReader
import os
import re
import ucto

from .alpino_brackets import escape_id, format_folia

alignable_characters = re.compile(r'[A-Za-zàéëüïóò]')
nonalignable_characters = re.compile(r'[^A-Za-zàéëüïóò]')

class TokenizedSentenceEmitter:
    offset = 0

    def __init__(self, sentences):
        self.sentences = sentences

    def get_sentences(self, part_text, part_offset = 0):
        if not self.sentences:
            return
        sentence = self.sentences[0] + '\n'

        remaining_sentence = sentence[self.offset:]

        alignable_text = nonalignable_characters.sub('', part_text)
        
        (sentence_length, part_offset, part_done) = self.get_part_length(remaining_sentence, alignable_text, part_offset)
        yield remaining_sentence[:sentence_length]
        if part_done:
            self.offset += sentence_length
        else:
            self.offset = 0
            # move to next sentence
            self.sentences = self.sentences[1:]
            yield from self.get_sentences(part_text, part_offset)
            

    def get_part_length(self, sentence, alignable_text, n = 0):
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
                    raise Exception(f"Alignment error at ({i}, {n})! Sentence: {sentence} Part: {alignable_text}")
                n += 1

        # the entire sentence matches
        return (len(sentence), n, False)

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
                    division = division_path[-1]
                    self.tokenizer.process(division.text)
                    sentence_emitter = TokenizedSentenceEmitter(list(self.tokenizer.sentences()))

                    for sentence in division.tostring(lambda part, text: self.add_word_metadata(sentence_emitter, part, text)).splitlines():
                        metadata = self.get_metadata(document, division_path)
                        # TODO: id from part if there is only one part?
                        sentence_id = self.determine_id(file_name, metadata, unique_ids)
                        yield (sentence, sentence_id, metadata)

    def add_word_metadata(self, sentence_emitter, part, text):
        if len(list(part.parts)) == 0:
            text = ''.join(sentence_emitter.get_sentences(part.text))
        
        attributes = self.get_element_metadata(part.attributes)
                
        if 'tei-tag' in attributes:
            tag = attributes['tei-tag']
            if tag == 'q':
                return self.modify_text(text, lambda text: f'" {text}"')

        if 'id' in attributes:
            identifier = attributes['id']
            # TODO: I think this is a bug in Alpino? "ERROR: something went wrong in saving the XML in stream($stream(140026222726096))!"
            #return self.modify_text(text, lambda text: f'[ @id {identifier} ] {text}')

        if 'lemma' in attributes and 'pos' in attributes:
            lemma = attributes['lemma']
            pos_tag = attributes['pos']
            return self.modify_text(text, lambda text: format_folia(lemma, pos_tag, text.strip()) + ' ')
                    
        return text

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

    def determine_id(self, file_name, metadata, unique_ids):
        if 'id' in metadata:
            sentence_id = escape_id(metadata['id'])
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

    def test_file(self, file_name):
        """
        Determine whether this is a TEI XML file
        """

        with open(file_name, encoding='utf-8') as file:
            for _ in range(0, 5):
                line = file.readline()
                if not line:
                    return False
                if '<TEI' in line:
                    return True

        return False
