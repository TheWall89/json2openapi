import yaml
from inducoapi.inducoapi import build_openapi


def test_get_employees_200():
    oapi = build_openapi("GET", "/employees", 200)
    with open("tests/test_get_employees_200.yaml") as f:
        assert yaml.safe_load(f.read()) == oapi


def test_get_employees_200_response():
    with open("examples/employees.json") as f:
        response = f.read()
    oapi = build_openapi("GET", "/employees", 200, response=response)
    with open("tests/test_get_employees_200_response.yaml") as f:
        assert yaml.safe_load(f.read()) == oapi


def test_get_employees_200_response_noexample():
    with open("examples/employees.json") as f:
        response = f.read()
    oapi = build_openapi("GET", "/employees", 200,
                         response=response, example=False)
    with open("tests/test_get_employees_200_response_noexample.yaml") as f:
        assert yaml.safe_load(f.read()) == oapi


def test_get_employees_200_response_yaml():
    with open("examples/employees.yaml") as f:
        response = f.read()
    oapi = build_openapi("GET", "/employees", 200,
                         response=response)
    with open("tests/test_get_employees_200_response.yaml") as f:
        assert yaml.safe_load(f.read()) == oapi


def test_get_employees_200_response_mediatype():
    with open("examples/employees.json") as f:
        response = f.read()
    oapi = build_openapi("GET", "/employees", 200,
                         response=response, media_type="application/yaml")
    with open("tests/test_get_employees_200_response_mediatype.yaml") as f:
        assert yaml.safe_load(f.read()) == oapi


def test_post_employees_201_request_response():
    with open("examples/new_employee_req.json") as f:
        request = f.read()
    with open("examples/new_employee_resp.json") as f:
        response = f.read()
    oapi = build_openapi("POST", "/employees", 201,
                         request=request, response=response)
    with open("tests/test_post_employees_201_request_response.yaml") as f:
        assert yaml.safe_load(f.read()) == oapi
