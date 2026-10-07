# pyxledger

A small Python client for the Xledger GraphQL API.

## Install

Add it to `dependencies` in your `pyproject.toml`:

```toml
"pyxledger @ git+https://github.com/asterisk-digital/pyxledger.git@main"
```

For development, run `uv sync`.

## Usage

```python
import pyxledger

client = pyxledger.Client("your_token")  # api_url defaults to "https://www.xledger.net/graphql"

customers = client.get_customers()
```

The `get_*` helpers page through all records. For other models use `client.get_all("model", "fields")`, or pass any GraphQL to `client.query()`.
