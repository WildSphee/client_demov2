import os
from pathlib import Path

import streamlit as st


def resolve_ref(openapi_spec, ref):
    ref_parts = ref.split("/")[1:]
    ref_obj = openapi_spec
    for part in ref_parts:
        ref_obj = ref_obj.get(part, {})
    return ref_obj


def get_parsed_schemas(schema):
    parsed_schema = parse_openapi_spec(schema)
    return parsed_schema[0]["request_model"]


def parse_openapi_spec(openapi_spec):
    api_data = []

    for path, path_data in openapi_spec["paths"].items():
        for request_type, operation_data in path_data.items():
            request_model = {"query_params": [], "body_params": []}

            if "parameters" in operation_data:
                for parameter in operation_data["parameters"]:
                    if "schema" in parameter and "$ref" in parameter["schema"]:
                        parameter["schema"] = resolve_ref(
                            openapi_spec, parameter["schema"]["$ref"]
                        )

                    if parameter["in"] == "query":
                        request_model["query_params"].append(parameter)

            if "requestBody" in operation_data:
                content = operation_data["requestBody"]["content"]
                if "multipart/form-data" in content:
                    schema_ref = content["multipart/form-data"]["schema"]["$ref"]
                    schema = resolve_ref(openapi_spec, schema_ref)

                    for prop_name, prop_data in schema["properties"].items():
                        param = {"name": prop_name, "in": "body", "schema": prop_data}
                        request_model["body_params"].append(param)

            api_data.append(
                {
                    "path": path,
                    "request_type": request_type,
                    "request_model": request_model,
                }
            )

    return api_data


def extract_request_model(request_model):
    required_params = []

    for param in request_model["query_params"]:
        required_param = {"type": "", "name": "", "choices": None, "value": None}
        assert "schema" in param
        if "enum" in param["schema"]:
            required_param["type"] = "enum"
            required_param["name"] = param["name"]
            required_param["choices"] = param["schema"]["enum"]
        elif "type" in param["schema"] and param["schema"]["type"] == "string":
            required_param["type"] = "string"
            required_param["name"] = param["name"]
        else:
            raise ValueError
        required_params.append(required_param)

    for param in request_model["body_params"]:
        required_param = {"type": "", "name": "", "value": None}

        assert "schema" in param
        assert "type" in param["schema"] and param["schema"]["type"] == "string"
        assert "format" in param["schema"] and param["schema"]["format"] == "binary"

        required_param["type"] = "file"
        required_param["name"] = param["name"]

        required_params.append(required_param)

    return required_params


def prepare_request(required_params):
    request = {"params": {}, "files": {}, "json": {}}

    for required_param in required_params:
        if required_param["type"] == "file":
            # Create a folder to store uploaded files
            if not os.path.exists("uploaded_files"):
                os.makedirs("uploaded_files")

            # Get the file name
            uploaded_file = required_param["value"]
            file_name = uploaded_file.name
            # Store the uploaded file in a folder
            with open(os.path.join("./uploaded_files", file_name), "wb") as f:
                f.write(uploaded_file.read())
            st.success(f"File '{file_name}' has been successfully uploaded and stored.")
            file_path = f"./uploaded_files/{file_name}"
            request["files"][required_param["name"]] = (
                Path(file_path).name,
                open(file_path, "rb"),
            )

        else:  # Param is string or enum
            request["params"][required_param["name"]] = required_param["value"]

    return request
