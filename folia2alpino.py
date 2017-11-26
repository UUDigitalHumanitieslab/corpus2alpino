#!/usr/bin/env python3
import sys
import argparse
from pynlpl.formats import folia


def main(argv):
    """
    Main entry point.
    """
    try:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.HelpFormatter)

        parser.add_argument(
            'file_names', metavar='FILE', type=str, nargs='+', help='FoLiA file(s) to parse')

        options = parser.parse_args(argv)

        for file_name in options.file_names:
            print("\n".join(get_sentences(file_name)))

    except Exception as exception:
        sys.stderr.write(repr(exception) + "\n")
        sys.stderr.write("for help use --help\n\n")
        raise exception


def get_sentences(file_name):
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
    # TODO: id and other strings should be escaped if needed
    return sentence.id + "|" + " ".join(get_word_string(word) for word in words)

def get_word_string(word):
    try:
        correction = word.getcorrection()
        original_text = word.text()
        return f"[ @add_lex {correction.text()} {original_text} ]" if correction.hastext() and correction.text() != original_text else original_text
    except folia.NoSuchAnnotation:
        return word.text()

main(sys.argv[1:])
