# pyxledger

A small Python client for the Xledger GraphQL API.

## Install

```bash
pip install git+https://github.com/asterisk-digital/pyxledger.git
```

It also works as a git submodule, importable as `pyxledger` from the folder it's checked out into:

```bash
git submodule add https://github.com/asterisk-digital/pyxledger.git ./src/pyxledger
```

## Usage

```python
import pyxledger

client = pyxledger.Client("your_token")  # api_url defaults to "https://www.xledger.net/graphql"

customers = client.get_customers()
```

The `get_*` helpers page through all records. For other models use `client.get_all("model", "fields")`, or pass any GraphQL to `client.query()`.
