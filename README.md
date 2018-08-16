[![Build Status](https://travis-ci.org/UUDigitalHumanitieslab/corpus2alpino.svg?branch=master)](https://travis-ci.org/UUDigitalHumanitieslab/corpus2alpino)

# FoLiA and TEI to Alpino XML

Converts [FoLiA](https://proycon.github.io/folia/) and [TEI](http://www.tei-c.org) XML files to [Alpino](www.let.rug.nl/vannoord/alp/Alpino) XML files. Each sentence in the input file is parsed separately.

## Usage

### Command Line

```bash
pip install corpus2alpino
corpus2alpino -s localhost:7001 folia.xml -o alpino.xml
```

Or from project root:

```bash
python -m corpus2alpino -s localhost:7001 folia.xml -o alpino.xml
```

### Library

```python
from corpus2alpino.converter import Converter
from corpus2alpino.annotators.alpino import AlpinoAnnotator
from corpus2alpino.collectors.filesystem import FilesystemCollector
from corpus2alpino.targets.memory import MemoryTarget
from corpus2alpino.writers.lassy import LassyWriter

alpino = AlpinoAnnotator("localhost", 7001)
converter = Converter(FilesystemCollector(["folia.xml"]),
    # Not needed when using the PaQuWriter
    annotators=[alpino],
    # This can also be ConsoleTarget, FilesystemTarget
    target=MemoryTarget(),
    # Set to merge treebanks, also possible to use PaQuWriter
    writer=LassyWriter(True))

# get the Alpino XML output, combined into one treebank XML file
parses = converter.convert()
print(''.join(parses)) # <treebank><alpino_ds ... /></treebank>
```

### Unit Test

```bash
python -m unittest
```

### Upload to PyPi

```bash
python setup.py sdist
twine upload dist/*
```

## Requirements

* [Alpino parser](http://www.let.rug.nl/vannoord/alp/Alpino) running as a server: `Alpino batch_command=alpino_server -notk server_port=7001`
* Python 3.6 or higher (developed using 3.6.3).
* [libfolia-dev](https://packages.ubuntu.com/bionic/libfolia-dev)
* [libicu-dev](https://packages.ubuntu.com/bionic/libicu-dev)
* [libxml2-dev](https://packages.ubuntu.com/bionic/libxml2-dev)
* [libticcutils2-dev](https://packages.ubuntu.com/bionic/libticcutils2-dev)
* [libucto-dev](https://packages.ubuntu.com/bionic/libucto-dev)
* [ucto](https://packages.ubuntu.com/bionic/ucto)
