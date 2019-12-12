#!/usr/bin/env python3
from typing import cast, Union

from corpus2alpino.abstracts import Target
from corpus2alpino.models import CollectedFile, Document
from corpus2alpino.targets.console import ConsoleTarget


class LogTarget:
    def __init__(self, target: Target):
        self.target = target
        self.document = Document(CollectedFile(
            '', 'log.txt', 'text/plain', ''), [])

    def write(self, content: str):
        self.target.write(self.document, content)

    def close(self):
        self.target.close()


class Log:
    def __init__(self, target: LogTarget, strict=False):
        self.strict = strict
        self.target = target

    def error(self, error: Exception):
        if self.strict:
            raise error
        else:
            self.target.write(str(error))

    def warning(self, warning: str):
        self.target.write(str(warning))

    def close(self):
        self.target.close()


class LogSingleton:
    _instance = None

    @staticmethod
    def get() -> Log:
        if LogSingleton._instance == None:
            LogSingleton._instance = Log(LogTarget(ConsoleTarget()))
        return cast(Log, LogSingleton._instance)

    @staticmethod
    def set(log: Log):
        if LogSingleton._instance:
            LogSingleton._instance.close()
        LogSingleton._instance = log
