#!/usr/bin/env python3
"""
Module for converting FoLiA xml files to Alpino XML files.
"""

import sys
import argparse
from pynlpl.formats import folia
from alpino_wrapper import AlpinoWrapper


def main(argv):
    """
    Main entry point.
    """

    try:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.HelpFormatter)

        parser.add_argument(
            'file_names', metavar='FILE', type=str, nargs='+', help='FoLiA file(s) to parse')
        parser.add_argument(
            '-s', '--server', metavar='SERVER', type=str, help='host:port of Alpino server')

        options = parser.parse_args(argv)
        if options.server != None:
            [host, port] = options.server.split(":")

        if options.server != None:
            for chunk in get_parses(options.file_names, host, port):
                print(chunk)
        else:
            sentences = get_sentences(options.file_names)
            print("\n".join(sentences))

    except Exception as exception:
        sys.stderr.write(repr(exception) + "\n")
        sys.stderr.write("for help use --help\n\n")
        raise exception


def get_parses(file_names, host, port):
    """
    Get the parses and a wrapping treebank xml structure.
    """

    wrapper = AlpinoWrapper(host, int(port))
    sentences = get_sentences(file_names)
    yield "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<treebank>"
    for sentence in sentences:
        yield wrapper.parse(sentence, True)
    yield "</treebank>"


def get_sentences(file_names):
    """
    Read a FoLiA file and return Alpino parsable sentences.
    """

    for file_name in file_names:
        doc = folia.Document(file=file_name)
        # doc.sentences() will skip quotes
        for paragraph in doc.paragraphs():
            for sentence in paragraph.sentences():
                yield get_sentence(sentence)


def get_sentence(sentence):
    """
    Convert a FoLiA sentence object to an Alpino compatible string to parse.
    """

    words = sentence.words()
    return escape_id(sentence.id) + "|" + " ".join(get_word_string(word) for word in words)


def get_word_string(word):
    """
    Get a string representing this word and any additional known properties to add to the parse.
    """

    try:
        correction = word.getcorrection()
        original_text = word.text()
        return f"[ @add_lex {escape_word(correction.text())} {escape_word(original_text)} ]" \
            if correction.hastext() and correction.text() != original_text \
            else escape_word(original_text)
    except folia.NoSuchAnnotation:
        return escape_word(word.text())


def escape_id(sentence_id):
    """
    Escape an id to be Alpino compatible.
    """

    return escape_word(sentence_id.replace("|", "_"))


def escape_word(text):
    """
    Escape a word to be Alpino compatible.
    """

    return text.replace("[", "\\[").replace("]", "\\]")


if __name__ == "__main__":
    main(sys.argv[1:])
