# FoLiA to Alpino XML

Converts [FoLiA](https://proycon.github.io/folia/) XML files to [Alpino](www.let.rug.nl/vannoord/alp/Alpino) XML files. Each sentence in the input FoLiA file is parsed separately.

## Usage

### Command Line
```bash
pip install folia2alpino
folia2alpino -s localhost:7001 folia.xml
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

## Requirements

* [Alpino parser](www.let.rug.nl/vannoord/alp/Alpino) running as a server.
* Python 3.6 or higher (developed using 3.6.1).
