#!/usr/bin/env python3
"""
Module for reading CHAT cha files to parsable utterances.
"""
from typing import cast, Dict, Iterable, List, Tuple
from chamd import ChatReader as ChatParser, ChatLine, ChatTier

import os
import re

from corpus2alpino.abstracts import Reader
from corpus2alpino.models import CollectedFile, Document, MetadataValue, Utterance

MANUAL_IDS = ['xsid', 'xuid']
UTTERANCE_NUMBER_ID = 'uttno'

class ChatReader(Reader):
    """
    Class for converting a CHAT file to document.
    """

    def read(self, collected_file: CollectedFile) -> Iterable[Document]:
        self.reader = ChatParser()
        chat = self.reader.read_string(
            collected_file.content, collected_file.filename)
        yield Document(collected_file,
                       list(self.parse_utterances(chat.lines)),
                       self.parse_metadata(chat.metadata))

    def parse_utterances(self, chat_lines: List[ChatLine]):
        number = 0
        for line in chat_lines:
            number += 1  # start numbering utterances from 1
            for id_override_key in MANUAL_IDS:
                try:
                    line.uttid = line.tiers[id_override_key].text
                    line.metadata['uttid'].text = line.uttid
                    break
                except KeyError:
                    pass

            yield Utterance(line.text,
                            str(line.uttid),
                            {
                                **self.parse_metadata(line.metadata),
                                **self.parse_tiers(line.tiers),
                                UTTERANCE_NUMBER_ID: MetadataValue(str(number), 'int')
                            },
                            int(line.metadata['uttstartlineno'].text))

    def parse_metadata(self, metadata) -> Dict[str, MetadataValue]:
        parsed = cast(Dict[str, MetadataValue], {})
        for (key, item) in metadata.items():
            parsed[key] = MetadataValue(item.text, item.value_type)

        return parsed

    def parse_tiers(self, tiers: Dict[str, ChatTier]) -> Dict[str, MetadataValue]:
        parsed = cast(Dict[str, MetadataValue], {})
        for tier in tiers.values():
            parsed[tier.name] = MetadataValue(tier.text)
        return parsed

    def test_file(self, file: CollectedFile):
        """
        Determine whether this is a CHAT file
        """

        return file.filename[-3:].upper() == 'CHA'
