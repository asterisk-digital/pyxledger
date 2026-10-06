from unittest.mock import MagicMock, patch

import pytest

from pyxledger import Client, PyXLedgerException


def mock_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


@patch("requests.post")
def test_query_sends_token_to_api_url(post):
    post.return_value = mock_response({"data": {}})

    Client("abc", api_url="https://demo.xledger.net/graphql").query("{ x }")

    post.assert_called_once_with(
        "https://demo.xledger.net/graphql",
        json={"query": "{ x }"},
        headers={"Authorization": "token abc"},
    )


def page(model, ids, has_next):
    edges = [{"cursor": f"c{i}", "node": {"dbId": i}} for i in ids]
    return mock_response({"data": {model: {"edges": edges, "pageInfo": {"hasNextPage": has_next}}}})


@patch("requests.post")
def test_get_all_data_flattens_edges(post):
    post.return_value = mock_response(
        {"data": {"projects": {"edges": [{"node": {"dbId": 1}}, {"node": {"dbId": 2}}]}}}
    )

    assert Client("abc").get_all_data("{ projects { edges { node { dbId } } } }", "projects") == [
        {"dbId": 1},
        {"dbId": 2},
    ]


@patch("requests.post")
def test_get_all_follows_cursors_until_last_page(post):
    post.side_effect = [page("projects", [1, 2], True), page("projects", [3], False)]

    assert Client("abc").get_projects() == [{"dbId": 1}, {"dbId": 2}, {"dbId": 3}]
    afters = [c.kwargs["json"]["variables"]["after"] for c in post.call_args_list]
    assert afters == [None, "c2"]


@patch("requests.post")
def test_get_all_fields_passes_type_name_as_variable(post):
    post.return_value = mock_response({"data": {"__type": {"fields": [{"name": "dbId"}, {"name": "code"}]}}})

    assert Client("abc").get_all_fields('Project") { evil }') == ["dbId", "code"]
    payload = post.call_args.kwargs["json"]
    assert payload["variables"] == {"name": 'Project") { evil }'}
    assert "evil" not in payload["query"]


@patch("requests.post")
def test_get_all_data_raises_on_graphql_errors(post):
    post.return_value = mock_response({"errors": [{"message": "bad query"}]})

    with pytest.raises(PyXLedgerException, match="bad query"):
        Client("abc").get_projects()
