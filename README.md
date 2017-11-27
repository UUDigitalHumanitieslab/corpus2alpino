# FoLiA to Alpino XML

Converts [FoLiA](https://proycon.github.io/folia/) XML files to [Alpino](www.let.rug.nl/vannoord/alp/Alpino) XML files. Each sentence in the input FoLiA file is parsed separately.

## Usage

### From the Command Line
```bash
pip install -r requirements.txt
python folia2alpino -s localhost:7001 folia.xml
```


### As Library
```python
from folia2alpino import folia2alpino

# generate sentences which can be used as input for Alpino
sentences = folia2alpino.get_sentences(["folia.xml"])
print(next(sentences)) # sentence id|Dit is een voorbeeld .

# get the Alpino XML files, combined into one treebank XML file
parses = folia2alpino.get_parses(["folia.xml"], host, port)
print("\n".join(parses)) # <treebank><alpino ... /></treebank>
```
## Requirements

* [Alpino parser](www.let.rug.nl/vannoord/alp/Alpino) running as a server.
* Python 3.6 or higher (developed using 3.6.1).
