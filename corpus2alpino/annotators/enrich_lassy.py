#!/usr/bin/env python3
"""
Allows enriching nodes of a Lassy annotation using a dictionary
"""
from typing import Dict

import csv
from lxml import etree

from corpus2alpino.abstracts import Annotator
from corpus2alpino.annotators.alpino import ANNOTATION_KEY
from corpus2alpino.log import LogSingleton
from corpus2alpino.models import Document, Utterance


class EnrichLassyAnnotator(Annotator):
    def __init__(self, enrichment_file: str):
        """Creates an annotator which will add additional attributes to
        nodes when they match the properties specified in an enrichment
        file.

        Arguments:
            enrichment_file {str} -- Path to a comma-separated enrichment file
            matching attributes columns should be prefixed with @, assignments
            without. For example the following CSV would match 
            <node pos="noun" num="pl" /> and add penn_pos="NNS":

            @pos,@num,penn_pos
            noun,pl,NNS
            noun,,NN
            pron,pl,NNPS
            pron,,NNP
            det,,DT

            Empty matchers are skipped, the first match is assigned.

        Raises:
            Exception: Exception is raised if it could not load or
            parse the enrichment file
        """
        with open(enrichment_file) as enrichment:
            dialect = csv.Sniffer().sniff(enrichment.read(1024))
            enrichment.seek(0)
            reader = csv.reader(enrichment, dialect)
            matchers = {}
            assigners = {}

            headers = next(reader)
            for i, header in enumerate(headers):
                if header.startswith("@"):
                    matchers[header[1:]] = i
                else:
                    assigners[header] = i

            self.enrichments = []

            for row in reader:
                enrichment = {}
                for i, value in enumerate(row):
                    self.enrichments.append(Enrichment(
                        {
                            key: row[index] for key, index in matchers.items() if row[index]
                        },
                        {
                            key: row[index] for key, index in assigners.items() if row[index]
                        }))

    def annotate(self, document: Document):
        for utterance in document.utterances:
            if not ANNOTATION_KEY in utterance.annotations:
                LogSingleton.get().error(
                    Exception("Lassy annotation missing for: {0}|{1}".format(utterance.id, utterance.text)))
            else:
                self.enrich_utterance(utterance)

    def enrich_utterance(self, utterance: Utterance):
        annotation = utterance.annotations[ANNOTATION_KEY]
        parse = etree.fromstring(annotation)
        modified = False
        for node in parse.iter("node"):
            for enrichment in self.enrichments:
                if enrichment.is_match(node):
                    modified = True
                    break
        if modified:
            utterance.annotations[ANNOTATION_KEY] = etree.tostring(
                parse, encoding='utf8').decode('utf8')


class Enrichment:
    def __init__(self, matchers: Dict[str, str], assigners: Dict[str, str]):
        self.matchers = matchers
        self.assigners = assigners

    def is_match(self, node) -> bool:
        """Check whether the Node lxml Element matches this enrichment.
        If this is the case, the values are assigned to this node

        Arguments:
            node {[type]} -- lxml Element of a Lassy node

        Returns:
            bool -- Whether this node matched
        """
        for key, value in self.matchers.items():
            try:
                if node.attrib[key] != value:
                    return False
            except KeyError:
                return False

        for key, value in self.assigners.items():
            node.attrib[key] = value

        return True
