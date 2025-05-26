# pyxledger

A simple Python library for interfacing with the XLedger API

## Setup

This is typically used as a submodule, which can be added to a python project as follows:

```(bash)
git submodule add git@github.com:intrix-as/pyxledger.git ./src/pyxledger
```

This will put pyxledger in the src/pyxledger folder of the project, which can then be imported as a module.

The library can be used as follows:

## Usage

```(python)
import pyxledger

url = 'xledger.net/graphql'
credentials = {
  'token': 'your_token'
}

client = pyxledger.Client(url, credentials)

# Getting customers is an example here
result = client.get_customers()
```
