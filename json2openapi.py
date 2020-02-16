#!/usr/bin/env python3

#  Copyright 2020 Matteo Pergolesi <matpergo [at] gmail [dot] com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse
import json
from json import JSONDecodeError
from typing import Dict, Tuple, Any, Union, List, Optional

import yaml
from openapi3 import OpenAPI
from openapi3.errors import SpecError

_example = False


def _get_type_ex(val: Any) -> Tuple[str, Any]:
    ex = val
    if val is None:
        # If no value is provided, assume string
        t = "string"
        ex = ""
    elif isinstance(val, str):
        t = "string"
    elif isinstance(val, int):
        t = "integer"
    elif isinstance(val, float):
        t = "number"
    elif isinstance(val, bool):
        t = "boolean"
    else:
        t = ""
        print("unknown type: {}, value: {}".format(type(val), val))

    global _example
    if _example:
        return {"type": t, "example": ex}
    else:
        return {"type": t}


def _gen_schema(data: Union[Dict, List]) -> Dict:
    if isinstance(data, dict):
        schema = {
            "type": "object",
            "properties": {}
        }
        for key, val in data.items():
            schema["properties"][key] = _gen_schema(val)
    elif isinstance(data, list):
        schema = {
            "type": "array",
            "items": {}
        }
        if data:
            schema["items"] = _gen_schema(data[0])
    else:
        schema = _get_type_ex(data)
    return schema


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


def _get_parser():
    descr = "Simple script to generate OpenAPI block from JSON request/response"
    parser = argparse.ArgumentParser("json2openapi.py", description=descr)
    parser.add_argument("method", type=str,
                        choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
                        help="HTTP request method", metavar="METHOD")
    parser.add_argument("path", type=str, help="URI path",
                        metavar="PATH")
    parser.add_argument("resp_code", type=int, help="HTTP response code",
                        metavar="CODE")
    parser.add_argument("--request", "-req", type=str,
                        help="Path to file containing request body")
    parser.add_argument("--response", "-rsp", type=str,
                        help="Path to file containing response body")
    parser.add_argument("--output", "-o", type=str, help="Output file")
    parser.add_argument("--no-example", "-ne", dest="example", default=True,
                        action="store_false",
                        help="Do not generate schema examples")
    parser.add_argument("--media-type", "-mt", type=str,
                        default="application/json",
                        help="Desired media type to be used.")
    return parser


def _load_file(file: str) -> Optional[Dict]:
    with open(file) as f:
        try:
            return json.load(f)
        except JSONDecodeError:
            f.seek(0)
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError:
                return None


def main():
    args = _get_parser().parse_args()
    global _example
    _example = args.example

    oapi = {
        "openapi": "3.0.0",
        "info": {
            "title": "Generated by json2openapi",
            "version": "v1",
        },
        "paths": {
            args.path: {
                args.method.lower(): {
                    "requestBody": None,
                    "responses": {
                        args.resp_code: {
                            "description": "",
                        }
                    }
                }
            }
        }
    }

    if args.request:
        request_load = _load_file(args.request)
        if request_load:
            oapi["paths"][args.path][args.method.lower()]["requestBody"] = {
                "content": {
                    args.media_type: {
                        "schema": _gen_schema(request_load)
                    }
                }
            }
        else:
            print("warning: {} looks not valid, skip request generation".
                  format(args.request))
    else:
        del oapi["paths"][args.path][args.method.lower()]["requestBody"]

    if args.response:
        response_load = _load_file(args.response)
        if response_load:
            oapi["paths"][args.path][args.method.lower()]["responses"][
                args.resp_code]["content"] = {
                args.media_type: {
                    "schema": _gen_schema(response_load)
                }
            }
        else:
            print("warning: {} looks not valid, skip response generation".
                  format(args.response))

    try:
        OpenAPI(oapi)
        print("\nOpenAPI looks valid\n")
    except SpecError as e:
        print("Validation error! {}".format(e.message))
        return

    if args.output:
        with open(args.output, "w") as o:
            yaml.dump(oapi, o, indent=2, Dumper=NoAliasDumper, sort_keys=False)
        print("Output written to {}".format(args.output))
    else:
        print("---")
        print(yaml.dump(oapi, indent=2, Dumper=NoAliasDumper, sort_keys=False))


if __name__ == '__main__':
    main()
