from typing import Any

import requests
from graphql import get_introspection_query, build_client_schema, is_object_type, is_input_object_type, is_enum_type

class PyXLedgerException(Exception):
    pass

class Client:
    def __init__(self, api_token: str, api_domain: str = "www.xledger.net"):
        self.api_url = f"https://{api_domain}/graphql"
        self.api_token = api_token

    # Raw query function
    def query_raw(self, query_string: str) -> requests.Response:
        headers = {"Authorization": f"token {self.api_token}"}

        response = requests.post(self.api_url, json={"query": query_string}, headers=headers)
        return response

    # Query function with error handling
    def query(self, query_string: str) -> Any:
        response = self.query_raw(query_string)
        response.raise_for_status()
        data = response.json()
        return data

    def get_all_data(self, query_string: str, model: str) -> list[dict]:
        data = self.query(query_string)

        if "errors" in data and data["errors"]:
            raise PyXLedgerException(data["errors"][0]["message"])

        # Extract the list of dictionaries
        result_dicts = []
        for entry in data["data"][model]["edges"]:
            # db_id = entry["node"]["dbId"]
            values = {key: value for key, value in entry["node"].items()}
            result_dicts.append(values)

        return result_dicts

    def get_all_fields(self, type_name: str) -> list[str]:
        """
        Returns a flat list of all field names for a given GraphQL type (non-recursive).
        """
        query = f"""
        {{
          __type(name: "{type_name}") {{
            name
            fields {{
              name
              type {{
                kind
                name
                ofType {{
                  kind
                  name
                  ofType {{
                    kind
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        data = self.query(query)
        fields = data["data"]["__type"]
        if not fields:
            raise PyXLedgerException(f"Type '{type_name}' not found in schema.")
        return [f["name"] for f in fields["fields"]]

    def get_customers(self):
        query_string = """
        {
          customers(last: 10000) {
            edges {
              node {
                dbId
                description
                code
                id
                description
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
              }
            }
          }
        }
        """

        return self.get_all_data(query_string, "customers")

    def get_contacts(self):
        query_string = """
        {
          contacts(last: 10000) {
            edges {
              node {
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
                }
            }
          }
        }
        """

        return self.get_all_data(query_string, "contacts")

    def get_suppliers(self):
        query_string = """
        {
          suppliers(last: 10000) {
            edges {
              node {
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
              }
            }
          }
        }
        """

        return self.get_all_data(query_string, "suppliers")

    def get_projects(self) -> list:
        query_string = """
        {
          projects(last: 10000) {
            edges {
              node {
                dbId
                code
                description

                owner {
                    dbId
                }
              }
            }
          }
        }
        """

        return self.get_all_data(query_string, "projects")

    def get_schema(self):
        """Return a GraphQLSchema object via introspection."""
        data = self.query(get_introspection_query())
        return build_client_schema(data["data"])

    def _enum_value_names(self, enum_type) -> list[str]:
        """
        Cross-version safe way to get enum value names.
        graphql-core v3: enum_type.values is a dict {name: GraphQLEnumValue}
        Some variants may expose it as an iterable of values.
        """
        vals = getattr(enum_type, "values", None)
        if vals is None:
            return []
        if isinstance(vals, dict):
            return list(vals.keys())
        # Fallback: iterable of enum values/strings
        names = []
        for v in vals:
            names.append(getattr(v, "name", str(v)))
        return names

    def find_everything_status(self, needle: str = "status"):
        """
        Search the whole schema for:
          - Fields whose name contains 'status'
          - Types with 'Status' in the name
          - Enum types and their values containing 'status'
          - Field arguments named like 'status'
        """
        schema = self.get_schema()
        type_map = schema.type_map

        needle_lower = needle.lower()
        result = {
            "fields": [],  # (parentType, fieldName, fieldType)
            "args": [],  # (parentType, fieldName, argName, argType)
            "types": [],  # typeName
            "enums": [],  # (enumType, [matchingValues])
        }

        for tname, gtype in type_map.items():
            if tname.startswith("__"):
                continue

            # Types whose names contain 'status'
            if "status" in tname.lower():
                result["types"].append(tname)

            # Object fields & their args
            if is_object_type(gtype):
                # In graphql-core v3, .fields is a dict {name: GraphQLField}
                fields = getattr(gtype, "fields", {}) or {}
                for fname, f in fields.items():
                    if needle_lower in fname.lower():
                        result["fields"].append((tname, fname, str(f.type)))
                    # Args is a dict {name: GraphQLArgument}
                    args = getattr(f, "args", {}) or {}
                    for aname, arg in args.items():
                        if needle_lower in aname.lower():
                            result["args"].append((tname, fname, aname, str(arg.type)))

            # Input object "fields" (used inside arguments)
            if is_input_object_type(gtype):
                in_fields = getattr(gtype, "fields", {}) or {}
                for iname, ifield in in_fields.items():
                    if needle_lower in iname.lower():
                        result["args"].append((tname, "(input)", iname, str(ifield.type)))

            # Enums
            if is_enum_type(gtype):
                value_names = self._enum_value_names(gtype)
                matches = [n for n in value_names if needle_lower in n.lower()]
                if matches or ("status" in tname.lower()):
                    result["enums"].append((tname, matches))

        return result
