#!/usr/bin/env python3
def format_add_lex(correction, word):
    """
    Lexical assignment to treat a given word as another word.
    """

    return f'[ @add_lex {escape_word(correction)} {escape_word(word)} ]'


def format_folia(lemma, pos_tag, word):
    """
    Lexical assignment of the lemma and postag.
    """

    return f'[ @folia {lemma} {pos_tag} {word} ]'


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
