# stac-vocab-api

## Getting started

Copy settings.py.tmpl and remove the tmpl extension. 
Fill in 
- CEDA_VOCAB_LOCATION

Create a virtualenv and install requirements
```bash
python -m venv venv
./venv/bin/activate
pip intall -r requirements.txt
```

## Running the server

```bash
uvicorn stac_vocab_api.owl.app:app --reload
```
