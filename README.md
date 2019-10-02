# Article Metadata Predictor

## Models

### Word2Vec Model 1 (`/w2v1`)

It's a country predictor from metadata
of an affiliation-contributor pair,
of from all such pairs coming from an XML article metadata.
It handles requests for:

* `/w2v1` (`GET`, `POST/JSON` or `POST/x-www-form`):
  Full message (all metadata concatenated) in the `msg` field;
* `/w2v1/fields` (`GET`, `POST/JSON` or `POST/form`):
  Fields of a single `<aff>-<contrib>` pair,
  all the ones in the `FIELDS` variable;
* `/w2v1/xml` (`POST/JSON`, `POST/XML` or `POST/multipart-form`):
  From Clea CLI output (JSON) or from the XML file itself,
  either in the request body or in the `xml` field.


## Development

In all cases, the model/dictionary files
(files `amp_.model` and `*.dict`)
should be in the repository root directory,
which should also be the current working directory.


### Local

```bash
python3.7 -m venv venv                  # Create virtualenv
source venv/bin/activate                # Activate the virtualenv
pip install -r source/requirements.txt  # Install the dependencies
python -m server.main                   # Debug the sanic server
```


### Docker

You can set the host/port
using the `AMP_HOST` and `AMP_PORT` environment variables.
To build and run, it's quite straightforward:

```bash
docker build -t amp -f infra/Dockerfile .
docker run --rm -p 8000:8000 -d amp
```
