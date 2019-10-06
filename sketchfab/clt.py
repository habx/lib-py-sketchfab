"""Sketfab client"""
import json
import logging
import os

from typing import List, Optional
import requests.auth
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from sketchfab.api import SFModelsApi, SFCollectionsApi
from sketchfab.models import SFCollection, SFModel


class SFCltAuth(requests.auth.AuthBase):
    """
    Authentication handling
    """

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers['Authorization'] = f'Token {self.token}'
        return r


class SFClient:
    def __init__(self, api_token: str = None):
        if not api_token:
            api_token = os.getenv('SKETCHFAB_API_TOKEN')

        if not api_token:
            conf_file = os.path.join(os.getenv('HOME'), '.sketchfab-py.json')
            if os.path.isfile(conf_file):
                logging.info("Loading api key from %s", conf_file)
                with open(conf_file) as f:
                    j = json.load(f)
                    api_token = j.get('apitoken')

        if not api_token:
            raise RuntimeError("You need to pass an API key or define the SKETCHFAB_API_TOKEN env var.")

        s = requests.Session()
        s.auth = SFCltAuth(api_token)
        retries = Retry(
            total=30,
            backoff_factor=0.5,
            method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],  # adding POST
            status_forcelist=[429, 502, 503, 504],  # Adding 429
        )
        s.mount('https://', HTTPAdapter(max_retries=retries))
        self._session = s

    @property
    def session(self):
        return self._session

    def models(self, sort_by: str = '-created_at', downloadable: bool = None, published: bool = None) -> List[SFModel]:
        return SFModelsApi.list_mines(
            self,
            sort_by=sort_by,
            downloadable=downloadable,
        )

    def collections(self) -> List[SFCollection]:
        return SFCollectionsApi.list(self)

    def create_collection(self, name: str, models: List[SFModel]) -> SFCollection:
        return SFCollectionsApi.create(self, name, models)

    def get_collection(self, name: str) -> Optional[SFCollection]:
        for c in self.collections():
            if c.name == name:
                return c
        return None
