"""DNS Authenticator for Selectel"""

import logging

import requests
import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

DEFAULT_AUTH_ENDPOINT = "https://cloud.api.selcloud.ru"
DEFAULT_API_ENDPOINT = "https://api.selectel.ru"


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Selectel

    This Authenticator uses the Selectel API to fulfill a dns-01 challenge.
    """

    description = ("Obtain certificates using a DNS TXT record "
                   "(if you are using Selectel for DNS).")
    ttl = 60

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
        self.__client = None
        self.__records = {}

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=120)
        add("credentials", help="Selectel credentials INI file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ("This plugin configures a DNS TXT record to respond "
                "to a dns-01 challenge using the Selected REST API.")

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "Selectel projects credentials INI file",
            {
                "account_id": "an ID of Selectel account.",
                "username": "the name of service account.",
                "password": "the password of service account.",
                "project_name": "the name of project.",
            },
        )

    def _perform(self, domain, validation_name, validation):
        zone_id = self._client.get_zone_id_by_domain(domain)
        rrset = self._client.get_zone_rrset_by_name(zone_id, validation_name)
        if rrset:
            rrset_id = rrset["id"]
            self._client.update_record(
                zone_id, rrset, validation_name, validation, self.ttl)
        else:
            rrset_id = self._client.add_record(
                zone_id, validation_name, validation, self.ttl)
        self.__records[validation] = rrset_id

    def _cleanup(self, domain, validation_name, validation):
        rrset_id = self.__records.get(validation, None)
        if not rrset_id:
            return
        zone_id = self._client.get_zone_id_by_domain(domain)
        self._client.del_record(zone_id, rrset_id)
        self.__records = {k: v
                          for k, v in self.__records.items()
                          if v != rrset_id}

    @property
    def _client(self):
        if not self.__client:
            self.__client = _SelectelClient(self.credentials)
        return self.__client


class _SelectelClient(object):
    """
    Encapsulates all communication with the Selectel API.
    """

    def __init__(self, credentials: dns_common.CredentialsConfiguration):
        self.auth_endpoint = (credentials.conf("auth_endpoint")
                              or DEFAULT_AUTH_ENDPOINT)
        self.api_endpoint = (credentials.conf("api_endpoint")
                             or DEFAULT_API_ENDPOINT)
        self.account_id = credentials.conf("account_id")
        self.username = credentials.conf("username")
        self.password = credentials.conf("password")
        self.project_name = credentials.conf("project_name")

        self.session = requests.session()

        self.__token = None

    def _r(self, method, uri, endpoint=None, *args, **kwargs):
        url = f"{endpoint or self.api_endpoint}{uri}"
        resp = self.session.request(method, url, *args, **kwargs)
        if resp.status_code >= 300:
            message_parts = [f"Failed to add validation record: "
                             f"status code {resp.status_code}"]
            answer = resp.json()
            try:
                message_parts.append(answer["error"])
            except LookupError:
                pass
            raise errors.PluginError(", ".join(message_parts))
        return resp

    def _api(self, method, uri, data=None, params=None):
        resp = self._r(method, uri,
                       headers={"X-Auth-Token": self._token},
                       params=params,
                       json=data)
        try:
            return resp.json()
        except requests.JSONDecodeError:
            return resp.content

    def _api_iter_result(self, method, uri, data=None, params=None):
        offset = 0
        if not params:
            params = {}
        while True:
            params.update({"offset": offset})
            answer = self._api(method, uri, data=data, params=params)
            for item in answer["result"]:
                yield item
            offset = answer["next_offset"]
            if offset == 0:
                break

    def _get_token(self):
        data = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": self.username,
                            "domain": {"name": self.account_id},
                            "password": self.password}}},
                "scope": {
                    "project": {
                        "name": self.project_name,
                        "domain": {"name": self.account_id}}}}}
        resp = self._r(
            "POST", f"/identity/v3/auth/tokens",
            endpoint=self.auth_endpoint,
            json=data)
        token = resp.headers.get("X-Subject-Token")
        if not token:
            raise errors.PluginError(f"No subject token "
                                     f"in authorization response.")
        return token

    @property
    def _token(self):
        if not self.__token:
            self.__token = self._get_token()
        return self.__token

    def get_zone_id_by_domain(self, domain):
        for zone in self._api_iter_result("GET", f"/domains/v2/zones"):
            if zone["name"] == domain + ".":
                return zone["id"]
        raise errors.PluginError(f"Zone not found for domain {domain}")

    def get_zone_rrset_by_name(self, zone_id, name):
        expected_name = name + "."
        for record in self._api_iter_result(
                "GET", f"/domains/v2/zones/{zone_id}/rrset"):
            if record["name"] == expected_name and record["type"] == "TXT":
                return record
        return None

    def add_record(self, zone_id, validation_name, validation, ttl):
        resp = self._api("POST", f"/domains/v2/zones/{zone_id}/rrset", data={
            "name": validation_name,
            "ttl": ttl,
            "type": "TXT",
            "records": [{"content": f'"{validation}"', "disabled": False}]
        })
        return resp["id"]

    def update_record(self, zone_id, rrset,
                      validation_name, validation, ttl):
        records = (rrset["records"]
                   + [{"content": f'"{validation}"', "disabled": False}])
        resp = self._api(
            "PATCH", f'/domains/v2/zones/{zone_id}/rrset/{rrset["id"]}', data={
                "name": validation_name,
                "ttl": ttl,
                "type": "TXT",
                "records": records,
            })
        return resp

    def del_record(self, zone_id, rrset_id):
        resp = self._api(
            "DELETE", f"/domains/v2/zones/{zone_id}/rrset/{rrset_id}")
        return resp
