#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from types import SimpleNamespace

APPROVERS_LIST = ["HadesArchitect"]


def parse_webhook_body(body):
    result = {}
    for line in body.split("\n"):
        if line.startswith("**Name:**"):
            result["name"] = line.split("**")[2].strip()
        if line.startswith("**Email:**"):
            result["email"] = line.split("**")[2].strip()
    return result


def input_to_obj(input_data):
    return json.loads(input_data, object_hook=lambda d: SimpleNamespace(**d))


def parse_webhook_data(input_data):
    input_data = input_to_obj(input_data)
    if (
        input_data.action == "labeled"
        and input_data.label.name == "accepted"
        and input_data.sender.login in APPROVERS_LIST
    ):
        return parse_webhook_body(input_data.issue.body)


def main():
    with open("input_example.json") as f:
        input_data = f.read()
    print(parse_webhook_data(input_data))


if __name__ == "__main__":
    main()
