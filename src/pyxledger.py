import requests


class Client:
    def __init__(self, api_url: str, credentials: dict):
        self.api_url = f'https://www.{api_url}'
        self.token = credentials['token']

    def get_all_data(self, query_string, model):
        headers = {
            "Authorization": f"token {self.token}"
        }

        response = requests.post(self.api_url, json={"query": query_string}, headers=headers)
        data = response.json()

        # Extract the list of dictionaries
        result_dict = {}
        for entry in data['data'][model]['edges']:
            db_id = entry['node']['dbId']
            values = {key: value for key, value in entry['node'].items()}
            result_dict[db_id] = values
        return result_dict

    def get_all_fields(self, type_name):
        query_string = '''
        {
          __type(name: "%s") {
            name
            fields {
              name
              type {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
        '''
        formatted_query = query_string % type_name

        headers = {
            "Authorization": f"token {self.token}"
        }

        response = requests.post(self.api_url, json={"query": formatted_query}, headers=headers)
        data = response.json()
        return data['data']['__type']['fields']

    def get_customers(self):
        query_string = '''
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
        '''

        return self.get_all_data(query_string, 'customers')

    def get_contacts(self):
        query_string = '''
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
        '''

        return self.get_all_data(query_string, 'contacts')

    def get_suppliers(self):
        query_string = '''
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
        '''

        return self.get_all_data(query_string, 'suppliers')

    def get_projects(self):
        query_string = '''
        {
          projects(last: 10000) {
            edges {
              node {
                dbId
                code
                description
                company {
                    companyNumber
                }
              }
            }
          }
        }
        '''

        return self.get_all_data(query_string, 'projects')
