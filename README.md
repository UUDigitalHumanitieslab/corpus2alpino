[![Actions Status](https://github.com/UUDigitalHumanitiesLab/corpus2alpino/workflows/Unit%20tests/badge.svg)](https://github.com/UUDigitalHumanitiesLab/corpus2alpino/actions)

[![PyPi/corpus2alpino](https://img.shields.io/pypi/v/corpus2alpino)](https://pypi.org/project/corpus2alpino/)

# CHAT, FoLiA, PaQu metadata, plaintext and TEI to Alpino XML or PaQu metadata format

Converts [CHAT](https://childes.talkbank.org/), [FoLiA](https://proycon.github.io/folia/), [PaQu metadata](https://dspace.library.uu.nl/bitstream/1874/356078/1/AnnCor_Annotation_2017_05_11_2017_05_11.pdf), plaintext and [TEI](http://www.tei-c.org) XML files to [Alpino](https://www.let.rug.nl/vannoord/alp/Alpino) XML files. Each sentence in the input file is parsed separately.

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

### Enrichment

It is possible to add custom properties to (existing) Lassy/Alpino files. This is done using a csv-file containing the node attributes and values to look for and the custom properties to assign.

For example:

```bash
python -m corpus2alpino tests/example_lassy.xml -e tests/enrichment.csv -of lassy
```

See [`corpus2alpino.annotators.enrich_lassy`](corpus2alpino/annotators/enrich_lassy.py) for more information.

## Development

### Unit Test

```bash
python -m unittest
```

### Upload to PyPi

See: https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives

Make sure `setuptools` and `wheel` are installed. Then from the virtualenv:

```bash
pip install build
python -m build
twine upload dist/*
```

## Requirements

* [Alpino parser](http://www.let.rug.nl/vannoord/alp/Alpino) running as a server: `Alpino batch_command=alpino_server -notk server_port=7001`
* Python 3.8 or higher
* [libfolia-dev](https://packages.ubuntu.com/bionic/libfolia-dev)
* [libxml2-dev](https://packages.ubuntu.com/bionic/libxml2-dev)

### Installation Instructions for Ubuntu

```bash
sudo apt install libfolia-dev libxml2-dev
pip install -r requirements.txt
```
