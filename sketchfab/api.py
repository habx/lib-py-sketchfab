"""
Sketchfab API
"""
import datetime
import json
import logging
import os
import tempfile
import zipfile
from typing import List, Dict, Any, Union, Optional

import requests

from sketchfab.models import SFModel, SFCollection

API_URL = 'https://api.sketchfab.com/v3'


class SFModelsApi:
    """Models management API"""

    @staticmethod
    def comment(clt: 'SketchFabClient', model: SFModel, msg: str) -> bool:
        """
        Post a comment on a model
        ([API doc](https://docs.sketchfab.com/data-api/v3/index.html#!/comments/post_v3_comments))
        """
        r = clt.session.post(
            f'{API_URL}/comments',
            data={'model': model.uid, 'body': msg},
        )
        r.raise_for_status()
        ok = r.status_code == 201

        if not ok:
            logging.warning("Could not add comment to model %s: %s", model.uid, r.content)

        return ok

    UPDATABLE_PROPERTIES: List[str] = ['name', 'description', 'isInspectable', 'isPublished', 'private']
    UPDATABLE_PROPERTIES_JSON: List[str] = ['tags', 'categories']

    @staticmethod
    def _prepare_update_data(model: SFModel) -> Dict[str, Union[str, bool]]:
        data = {}
        for prop_name in model.modified:
            value = model.json[prop_name]
            if prop_name in SFModelsApi.UPDATABLE_PROPERTIES:
                data[prop_name] = value
            elif prop_name in SFModelsApi.UPDATABLE_PROPERTIES_JSON:
                data[prop_name] = json.dumps(value)
            # Some more specific logic might appear later
        return data

    @staticmethod
    def update_model(
            clt: 'SketchFabClient',
            model: SFModel,
    ) -> bool:

        data = SFModelsApi._prepare_update_data(model)

        r = clt.session.patch(
            f'{API_URL}/models/{model.uid}',
            data=data,
        )
        model.modified = []
        ok = r.status_code == 204
        return ok

    @staticmethod
    def get_model(clt: 'SketchFabClient', uid: str) -> Optional[SFModel]:
        r = clt.session.get(
            f'{API_URL}/models/{uid}'
        )
        if r.status_code == 200:
            j = json.loads(r.content)
            return SFModel(j, clt)
        else:
            return None

    @staticmethod
    def _list_prepare_params_common(
            downloadable: bool = None,
            sort_by: str = None,
            collection: SFCollection = None,
            published_since: datetime.date = None,  # public only
    ) -> Dict[str, Union[bool, str]]:
        params = {
            'type': 'models',
        }
        if downloadable is not None:
            params['downloadable'] = downloadable
        if collection:
            params['collection'] = collection.uid
        if sort_by:
            params['sort_by'] = sort_by
        if published_since:
            params['published_since'] = published_since.strftime("%Y-%m-%d")
        return params

    @staticmethod
    def list_public(
            clt: 'SketchFabClient',
            sort_by: str = None,
            downloadable: bool = None,
            published_since: datetime.datetime = None
    ) -> List[SFModel]:
        params = SFModelsApi._list_prepare_params_common(
            downloadable=downloadable,
            sort_by=sort_by,
            published_since=published_since,
        )
        req = requests.PreparedRequest()
        req.prepare_url(f'{API_URL}/search', params)
        r = clt.session.get(req.url)
        r.raise_for_status()
        data = r.json()
        return [SFModel(m, clt) for m in data['results']]

    @staticmethod
    def list_mines(
            clt: 'SketchFabClient',
            sort_by: str = None,
            downloadable: bool = None,
            collection: SFCollection = None
    ) -> List[SFModel]:

        # Using a prepared request is the simplest way to build an URL
        params = SFModelsApi._list_prepare_params_common(
            sort_by=sort_by,
            downloadable=downloadable,
            collection=collection,
        )
        req = requests.PreparedRequest()
        req.prepare_url(f'{API_URL}/me/search', params)
        r = clt.session.get(req.url)
        r.raise_for_status()
        data = r.json()
        return [SFModel(m, clt) for m in data['results']]

    @staticmethod
    def upload_model(
            clt: 'SketchFabClient',
            file_path: str,
            model: SFModel = None
    ) -> Optional[SFModel]:
        """
        https://docs.sketchfab.com/data-api/v3/index.html#!/models/post_v3_models
        :param clt: Client
        :param file_path: File to upload
        :param model: Optional model description
        :return: The model
        """
        if not model:
            model = SFModel()

        params = SFModelsApi._prepare_update_data(model)

        with open(file_path, 'rb') as f:
            r = clt.session.post(
                f'{API_URL}/models',
                data=params,
                files={'modelFile': f}
            )
            r.raise_for_status()
            if r.status_code == 201:
                j = json.loads(r.content)
                model.json['uid'] = j['uid']
                model.modified = []
                return model
            return None

    @staticmethod
    def download(clt: 'SketchFabClient', model: SFModel) -> str:
        data = clt.session.get(f'{API_URL}/models/{model.uid}/download').json()
        url_download = data['gltf']['url']
        with requests.get(url_download, stream=True) as r:
            r.raise_for_status()
            suffix = f'_{model.uid}'
            if r.headers.get('content-type') == 'application/zip':
                suffix += '.zip'
            _, path = tempfile.mkstemp(prefix='sketchfab_', suffix=suffix)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            return path

    @staticmethod
    def download_to_dir(clt: 'SketchFabClient', model: SFModel) -> str:
        zf = SFModelsApi.download(clt, model)
        with zipfile.ZipFile(zf, 'r') as zip_ref:
            path = tempfile.mkdtemp(prefix='sketchfab_', suffix=f'_{model.uid}')
            zip_ref.extractall(path)
        os.remove(zf)
        return path


class SFCollectionsApi:
    """Collections management API"""

    @staticmethod
    def list(clt: 'SketchFabClient') -> List[SFCollection]:
        r = clt.session.get(f'{API_URL}/me/collections')
        r.raise_for_status()
        data = r.json()
        return [SFCollection(m, clt) for m in data['results']]

    @staticmethod
    def create(clt, name: str, models: List[SFModel]) -> 'SFCollection':
        r = clt.session.post(
            f'{API_URL}/collections',
            json={
                'name': name,
                'models': [m.uid for m in models]
            },
        )
        r.raise_for_status()
        r = requests.get(r.headers['Location'])
        return SFCollection(r.json())

    UPDATABLE_PROPERTIES: List[str] = ['name']

    @staticmethod
    def _prepare_update_data(collection: SFCollection) -> Dict[str, Union[str, bool]]:
        data = {}
        for prop_name in collection.modified:
            value = collection.json[prop_name]
            if prop_name in SFModelsApi.UPDATABLE_PROPERTIES:
                data[prop_name] = value
            # Some more specific logic might appear later
        return data

    @staticmethod
    def update(clt, collection: SFCollection) -> bool:
        r = clt.session.patch(
            f'{API_URL}/collections/{collection.uid}',
            data=SFCollectionsApi._prepare_update_data(collection),
        )
        ok = r.status_code / 100 == 2
        if not ok:
            logging.warning("Failed to update collection: %s", r.content)
        return ok

    @staticmethod
    def add_model(clt, collection: SFCollection, model: SFModel) -> bool:
        r = clt.session.post(
            f'{API_URL}/collections/{collection.uid}/models',
            json={'models': [model.uid]},
        )
        ok = r.status_code == requests.codes.created

        if not ok:
            logging.warning("Could not add model %s to collection %s: %s", model.uid, collection.uid, r.content)

        return ok

    @staticmethod
    def remove_model(clt, collection: SFCollection, model: SFModel) -> bool:
        r = clt.session.delete(
            f'{API_URL}/collections/{collection.uid}/models',
            json={'models': [model.uid]},
        )
        ok = r.status_code == 204

        if not ok:
            logging.warning("Could not remove model %s from collection %s: %s", model.uid, collection.uid, r.content)

        return ok

    @staticmethod
    def list_models(clt: 'SketchFabClient', collection: SFCollection) -> List[SFModel]:
        return SFModelsApi.list_mines(clt, collection=collection)

    @staticmethod
    def list_models_broken(clt: 'SketchFabClient', collection: SFCollection) -> List[SFModel]:
        """
        *Should* list all models of the collection but instead always returns an empty list
        :param clt: Client
        :param collection: Collection
        :return: List of models
        """
        data = clt.session.get(
            f'{API_URL}/collections/{collection.uid}/models',
        ).json()
        return [SFModel(m, clt) for m in data['results']]
