from typing import Any

import requests
from graphql import build_client_schema, get_introspection_query

from .exceptions import PyXLedgerException

CUSTOMER_FIELDS = """
dbId
description
code
id
address {
    zipCode
    streetAddress
    place
    country {
        code
        description
    }
    state {
        description
        code
    }
}
company {
    companyNumber
}
contact {
    dbId
}
"""

CONTACT_FIELDS = """
dbId
phone
email
firstName
middleName
lastName
aliasName
companyName
company {
    companyNumber
    description
}
"""

SUPPLIER_FIELDS = """
dbId
description
code
address {
    zipCode
    streetAddress
    place
    country {
        code
        description
    }
    state {
        description
        code
    }
}
company {
    companyNumber
}
contact {
    dbId
}
"""

PROJECT_FIELDS = """
dbId
code
description
owner {
    dbId
}
"""


class Client:
    def __init__(self, api_token: str, api_url: str = "https://www.xledger.net/graphql"):
        self.api_url = api_url
        self.api_token = api_token

    def query_raw(self, query_string: str, variables: dict | None = None) -> requests.Response:
        headers = {"Authorization": f"token {self.api_token}"}
        payload = {"query": query_string}
        if variables:
            payload["variables"] = variables

        return requests.post(self.api_url, json=payload, headers=headers)

    def query(self, query_string: str, variables: dict | None = None) -> Any:
        response = self.query_raw(query_string, variables)
        response.raise_for_status()
        return response.json()

    def _query_checked(self, query_string: str, variables: dict | None = None) -> dict:
        data = self.query(query_string, variables)
        if data.get("errors"):
            raise PyXLedgerException(data["errors"][0]["message"])
        return data["data"]

    def get_all_data(self, query_string: str, model: str) -> list[dict]:
        """Run a single query and return the nodes of `model`. Does not paginate; see `get_all`."""
        data = self._query_checked(query_string)
        return [edge["node"] for edge in data[model]["edges"]]

    def get_all(self, model: str, fields: str, page_size: int = 1000) -> list[dict]:
        """Fetch every node of `model` (e.g. "customers"), following cursors until the last page."""
        query_string = f"""
        query ($first: Int, $after: String) {{
          {model}(first: $first, after: $after) {{
            edges {{
              cursor
              node {{ {fields} }}
            }}
            pageInfo {{ hasNextPage }}
          }}
        }}
        """
        nodes = []
        after = None
        while True:
            page = self._query_checked(query_string, {"first": page_size, "after": after})[model]
            nodes.extend(edge["node"] for edge in page["edges"])
            if not page["pageInfo"]["hasNextPage"] or not page["edges"]:
                return nodes
            after = page["edges"][-1]["cursor"]

    def get_all_fields(self, type_name: str) -> list[str]:
        """Return the field names of a GraphQL type (non-recursive)."""
        query_string = """
        query ($name: String!) {
          __type(name: $name) {
            fields { name }
          }
        }
        """
        gql_type = self._query_checked(query_string, {"name": type_name})["__type"]
        if not gql_type:
            raise PyXLedgerException(f"Type '{type_name}' not found in schema.")
        return [f["name"] for f in gql_type["fields"]]

    def get_customers(self) -> list[dict]:
        return self.get_all("customers", CUSTOMER_FIELDS)

    def get_contacts(self) -> list[dict]:
        return self.get_all("contacts", CONTACT_FIELDS)

    def get_suppliers(self) -> list[dict]:
        return self.get_all("suppliers", SUPPLIER_FIELDS)

    def get_projects(self) -> list[dict]:
        return self.get_all("projects", PROJECT_FIELDS)

    def get_schema(self):
        """Return a GraphQLSchema object via introspection."""
        data = self.query(get_introspection_query())
        return build_client_schema(data["data"])
