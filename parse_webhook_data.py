#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from types import SimpleNamespace

import requests

APPROVERS_LIST = ["HadesArchitect"]
# https://github.com/settings/tokens
GH_TOKEN = os.getenv("GH_TOKEN")
BOT_MESSAGE = "Hey I'm badgr bot and I'm about to issue a badge for **{name}**"


class WebhookData:
    def __init__(self, *args, **kwargs):
        _ = args
        self.input_data = self.input_to_obj(kwargs.get("input_data", None))
        self.issue_body = self.input_data.issue.body
        self.issue_url = self.input_data.issue.url
        self.student_name = ""
        self.student_email = ""

    def input_to_obj(self, input_data):
        return json.loads(input_data, object_hook=lambda d: SimpleNamespace(**d))

    def parse_webhook_body(self):
        for line in self.issue_body.split("\n"):
            name_regex = re.match(
                r"([^\w]*[Nn][Aa][Mm][Ee][^\w]*)(?P<name>[\w\s.]+)", line
            )
            email_regex = re.match(
                r"([^\w]*[Ee][Mm][Aa][Ii][Ll][^\w]*)(?P<email>\S+@\S+)", line
            )
            if name_regex:
                self.student_name = name_regex.group("name").strip()
            if email_regex:
                self.student_email = email_regex.group("email").strip()
        return {"name": self.student_name, "email": self.student_email}

    def parse_webhook_data(self):
        if (
            self.input_data.action == "labeled"
            and self.input_data.label.name == "accepted"
            and self.input_data.sender.login in APPROVERS_LIST
        ):
            return self.parse_webhook_body()

    def comment_create(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GH_TOKEN}",
        }
        url = f"{ self.issue_url }/comments"
        payload = {"body": BOT_MESSAGE.format(name=self.student_name)}
        r = requests.post(url, json=payload, headers=headers)
        return r.status_code


def main():
    with open("input_example.json") as f:
        input_data = f.read()

    wd = WebhookData(input_data=input_data)
    result = wd.parse_webhook_data()
    if "name" in result:
        wd.comment_create()


if __name__ == "__main__":
    main()
