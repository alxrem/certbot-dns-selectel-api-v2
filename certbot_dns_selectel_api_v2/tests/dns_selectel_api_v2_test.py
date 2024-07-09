"""Tests for certbot_dns_selectel_api_v2.dns_selectel_api_v2."""

import json
import tempfile
import unittest

import requests_mock
from certbot.plugins import dns_common
from certbot.plugins.dns_test_common import DOMAIN

FAKE_ACCOUNT = "expected_account_id"
FAKE_PROJECT = "expected_project_name"
FAKE_USER = "expected_remote_user"
FAKE_PW = "expected_password"
FAKE_AUTH_ENDPOINT = "mock://auth_endpoint"
FAKE_API_ENDPOINT = "mock://api_endpoint"


class SelectelClientTest(unittest.TestCase):
    def setUp(self):
        from certbot_dns_selectel_api_v2.dns_selectel_api_v2 import \
            _SelectelClient
        with tempfile.NamedTemporaryFile("w+") as f:
            f.write(f"""
            auth_endpoint = "{FAKE_AUTH_ENDPOINT}"
            api_endpoint = "{FAKE_API_ENDPOINT}"
            account_id = "{FAKE_ACCOUNT}"
            username = "{FAKE_USER}"
            password = "{FAKE_PW}"
            project_name = "{FAKE_PROJECT}"
            """)
            f.seek(0)
            credentials = dns_common.CredentialsConfiguration(f.name)
        self.adapter = requests_mock.Adapter()
        self.client = _SelectelClient(credentials)
        self.client.session.mount("mock://", self.adapter)

    def test_get_zone_id_by_domain(self):
        expected_token = "expected_token"

        def auth_request_matcher(req):
            data = json.loads(req.text)
            expected_data = {
                "auth": {
                    "identity": {
                        "methods": ["password"],
                        "password": {
                            "user": {
                                "name": FAKE_USER,
                                "domain": {"name": FAKE_ACCOUNT},
                                "password": FAKE_PW}}},
                    "scope": {
                        "project": {
                            "name": FAKE_PROJECT,
                            "domain": {"name": FAKE_ACCOUNT}}}}}
            return data == expected_data

        def auth_token_matcher(req):
            return req.headers.get("X-Auth-Token") == expected_token

        self.adapter.register_uri(
            "POST", "mock://auth_endpoint/identity/v3/auth/tokens",
            headers={"X-Subject-Token": expected_token},
            additional_matcher=auth_request_matcher,
        )
        self.adapter.register_uri(
            "GET", "mock://api_endpoint/domains/v2/zones",
            additional_matcher=auth_token_matcher,
            text="""
            {
              "count": 2,
              "next_offset": 0,
              "result": [
                {
                  "id": "ed350b64-3c0a-4adf-b2e2-a0b54b9d8b42",
                  "name": "example.com.",
                  "project_id": "2345221d41d04c0daf70f17b02468f46",
                  "created_at": "2024-04-29T22:39:28+00:00",
                  "updated_at": "2024-04-29T22:39:29+00:00",
                  "comment": null,
                  "disabled": false,
                  "protected": false,
                  "delegation_checked_at": "2024-07-06T12:05:29+00:00",
                  "last_delegated_at": "2024-07-06T12:05:29+00:00",
                  "last_check_status": true
                },
                {
                  "id": "6453f393-ab75-4fb6-b608-3774fef11108",
                  "name": "example.org.",
                  "project_id": "2345221d41d04c0daf70f17b02468f46",
                  "created_at": "2024-04-28T20:31:42+00:00",
                  "updated_at": "2024-04-29T22:39:29+00:00",
                  "comment": null,
                  "disabled": false,
                  "protected": false,
                  "delegation_checked_at": "2024-07-06T12:05:30+00:00",
                  "last_delegated_at": "2024-07-06T12:05:30+00:00",
                  "last_check_status": true
                }
              ]
            }
            """
        )

        self.client.get_zone_id_by_domain(DOMAIN)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
