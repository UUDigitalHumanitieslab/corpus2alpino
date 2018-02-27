[![Build Status](https://travis-ci.org/UUDigitalHumanitieslab/folia2alpino.svg?branch=master)](https://travis-ci.org/UUDigitalHumanitieslab/folia2alpino)

# FoLiA and TEI to Alpino XML

Converts [FoLiA](https://proycon.github.io/folia/) and [TEI](http://www.tei-c.org) XML files to [Alpino](www.let.rug.nl/vannoord/alp/Alpino) XML files. Each sentence in the input file is parsed separately.

## Usage

### Command Line
```bash
pip install folia2alpino
folia2alpino -s localhost:7001 folia.xml -o alpino.xml
```

### Library
```python
from folia2alpino.converter import Converter
from folia2alpino.alpino_wrappers import AlpinoServiceWrapper

alpino = AlpinoServiceWrapper("localhost", 7001)
converter = Converter(alpino)

# generate sentences which can be used as input for Alpino
sentences = converter.get_sentences(["folia.xml"])
print(next(sentences)) # sentence id|Dit is een voorbeeld .

# get the Alpino XML files, combined into one treebank XML file
parses = converter.get_parses(["folia.xml"])
print("\n".join(parses)) # <treebank><alpino ... /></treebank>
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
* Python 3.6 or higher (developed using 3.6.1).
* [libfolia-dev](https://packages.ubuntu.com/bionic/libfolia-dev)
* [libticcutils2-dev](https://packages.ubuntu.com/bionic/libticcutils2-dev)
* [libucto-dev](https://packages.ubuntu.com/bionic/libucto-dev)
* [ucto](https://packages.ubuntu.com/bionic/ucto)

