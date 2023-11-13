import ast

from fastapi.testclient import TestClient

from app.main import create_app

VALID_CLASS_DEF = """
class Foo:
    def bar(self, x: int) -> str:
        pass
"""

VALID_METHOD_DEF = """
def foo():
    pass
"""

ENDPOINT = "/api/code/retrieve/"


def test_retrieval_api_code_ast(tmpdir):
    # GIVEN
    valid_python_file = tmpdir / "valid.py"
    valid_python_file.write_text(f"{VALID_CLASS_DEF}\n{VALID_METHOD_DEF}", encoding="utf-8")

    # WHEN
    client = TestClient(create_app(index_root=tmpdir))
    response = client.post(url=ENDPOINT, json={"entities": ["Foo", "foo"]})

    # THEN
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json["data"]) == 2

    actual_class_def_ast = ast.parse(response_json["data"][0])
    expected_class_def_ast = ast.parse(VALID_CLASS_DEF)
    assert ast.dump(actual_class_def_ast) == ast.dump(expected_class_def_ast)

    actual_method_def_ast = ast.parse(response_json["data"][1])
    expected_method_def_ast = ast.parse(VALID_METHOD_DEF)
    assert ast.dump(actual_method_def_ast) == ast.dump(expected_method_def_ast)


def test_retrieval_api_invalid_files(tmpdir):
    # GIVEN
    valid_python_file = tmpdir / "valid.py"
    valid_python_file.write_text(VALID_CLASS_DEF, encoding="utf-8")

    invalid_python_file = tmpdir / "invalid.py"
    invalid_python_file.write_text("baz = ", encoding="utf-8")

    # WHEN
    client = TestClient(create_app(index_root=tmpdir))
    response = client.post(url=ENDPOINT, json={"entities": ["Foo"]})

    # THEN
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


def test_retrieval_api_ignored_files(tmpdir):
    # GIVEN
    valid_python_file = tmpdir / "valid.py"
    valid_python_file.write_text(VALID_CLASS_DEF, encoding="utf-8")

    ignored_file = tmpdir / "ignored.md"
    ignored_file.write_text("# Baz", encoding="utf-8")

    # WHEN
    client = TestClient(create_app(index_root=tmpdir))
    response = client.post(url=ENDPOINT, json={"entities": ["Foo"]})

    # THEN
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


def test_retrieval_api_invalid_payload(tmpdir):
    # GIVEN
    invalid_payload = {"entities": "Foo"}

    # WHEN
    client = TestClient(create_app(tmpdir))
    response = client.post(url=ENDPOINT, json=invalid_payload)

    # THEN
    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"][0]["input"] == "Foo"
    assert response_json["detail"][0]["loc"] == ["body", "entities"]
    assert response_json["detail"][0]["msg"] == "Input should be a valid list"
    assert response_json["detail"][0]["type"] == "list_type"
