# stac-vocab-api

## Getting started

Copy `_config/config.py.tmpl` and remove the tmpl extension. 
Fill in:
- `CEDA_VOCAB_LOCATION` - An example data file is included at `data/ceda.xml`.

Create a virtualenv and install requirements
```bash
python -m venv venv
./venv/bin/activate
pip intall -r requirements.txt
pip install -e .
pip install .[server]
```

## Running the server

```bash
venv/bin/uvicorn stac_vocab_api.app:app --reload
```

## Checking the server
`http://localhost:8000/concept/search/?input=CNRM-CM6-1-HR`
