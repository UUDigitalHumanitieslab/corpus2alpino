#!/usr/bin/env python3
"""
Allows enriching nodes of a Lassy annotation using a dictionary
"""
from typing import cast, Dict, List

import csv
import logging
from lxml import etree

from corpus2alpino.abstracts import Annotator
from corpus2alpino.annotators.alpino import ANNOTATION_KEY
from corpus2alpino.models import Document, Utterance


class EnrichLassyAnnotator(Annotator):
    def __init__(self, enrichment_file: str):
        """Creates an annotator which will add additional attributes to
        nodes when they match the properties specified in an enrichment
        file.

        Arguments:
            enrichment_file {str} -- Path to a comma-separated enrichment file.
            The enrichment file consists of columns with attributes to match
            on nodes and attributes which will be assigned on match.
            The column names containing the matching attributes should be prefixed with @,
            assignments should be without.

            For example the following CSV would match @pos="noun" and @num="pl"
            <node pos="noun" num="pl" /> and add penn_pos="NNS":

            @pos,@num,penn_pos
            noun,pl,NNS
            noun,,NN
            pron,pl,NNPS
            pron,,NNP
            det,,DT

            Empty attribute matchers are ignored: they always match,
            even if the attribute is not on the node.
            Only the properties in the first matching row are assigned to the node.

        Raises:
            Exception: Exception is raised if it could not load or
            parse the enrichment file
        """
        with open(enrichment_file) as enrichment:
            dialect = csv.Sniffer().sniff(enrichment.read(1024))
            enrichment.seek(0)
            reader = csv.reader(enrichment, dialect)

            # column numbers for the property names
            matchers = {}
            assigners = {}

            headers = next(reader)
            for i, header in enumerate(headers):
                if header.startswith("@"):
                    matchers[header[1:]] = i
                else:
                    assigners[header] = i

            self.enrichments = cast(List[Enrichment], [])

            for row in reader:
                for i, value in enumerate(row):
                    # get the cell values for the matchers and the assignments using
                    # dictionary comprehensions
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
                logging.getLogger().error(
                    Exception("Lassy annotation missing for: {0}|{1}".format(utterance.id, utterance.text)))
            else:
                self.enrich_utterance(utterance)

    def enrich_utterance(self, utterance: Utterance):
        annotation = utterance.annotations[ANNOTATION_KEY]
        parse = etree.fromstring(annotation)
        modified = False
        for node in parse.iter("node"):
            for enrichment in self.enrichments:
                if enrichment.assign_match(node):
                    modified = True
                    break
        if modified:
            # store the updated lassy xml with the enriched nodes
            utterance.annotations[ANNOTATION_KEY] = etree.tostring(
                parse, encoding='utf8').decode('utf8')


class Enrichment:
    def __init__(self, matchers: Dict[str, str], assigners: Dict[str, str]):
        self.matchers = matchers
        self.assigners = assigners

    def assign_match(self, node) -> bool:
        """Check whether the Node lxml Element matches this enrichment.
        If this is the case, the values are assigned to this node.

        Arguments:
            node {[type]} -- lxml Element of a Lassy node

        Returns:
            bool -- Whether this node matched
        """
        for key, value in self.matchers.items():
            if node.attrib.get(key) != value:
                return False

        for key, value in self.assigners.items():
            node.attrib[key] = value

        return True
