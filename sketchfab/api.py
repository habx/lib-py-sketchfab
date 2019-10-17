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
        ok = r.status_code == 201

        if not ok:
            logging.warning("Could not add comment to model %s: %s", model.uid, r.content)

        return ok

    @staticmethod
    def update_model(
            clt: 'SketchFabClient',
            model: SFModel,

            # We should turn it into a class that can be re-used at creation and update
            name: str = None,
            is_inspectable: bool = None,
            is_published: bool = None,
            description: str = None,
    ) -> bool:
        data = {}
        if name:
            data['name'] = name
        if is_inspectable is not None:
            data['isInspectable'] = True
        if is_published is not None:
            data['isPublished'] = True
        if description is not None:
            data['description'] = description

        r = clt.session.patch(
            f'{API_URL}/models/{model.uid}',
            input=data,
        )
        return r.status_code == 204

    @staticmethod
    def get_model(clt: 'SketchFabClient', uid: str) -> Optional[SFModel]:
        r = clt.session.get(
            f'{API_URL}/models/{uid}'
        )
        if r.status_code == 200:
            return SFModel(r.json, clt)
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
        data = clt.session.get(req.url).json()
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
        data = clt.session.get(req.url).json()
        return [SFModel(m, clt) for m in data['results']]

    @staticmethod
    def _prepare_model_params(model: SFModel) -> Dict[str, Union[str, bool]]:
        params = {}
        if model.name:
            params['name'] = model.name

        return params

    @staticmethod
    def upload_model(
            clt: 'SketchFabClient',
            file_path: str,
            private=True,
            model: SFModel = None
    ) -> Optional[SFModel]:
        """
        https://docs.sketchfab.com/data-api/v3/index.html#!/models/post_v3_models
        :param clt: Client
        :param file_path: File to upload
        :param model: Optional model description
        :param private: If the model should be private (activated by default)
        :return: The model
        """
        if not model:
            model = SFModel()

        params = SFModelsApi._prepare_model_params(model)
        if private:
            params['private'] = private

        with open(file_path, 'rb') as f:
            r = clt.session.post(
                f'{API_URL}/models',
                data=params,
                files={'modelFile': f}
            )
            if r.status_code == 400:
                logging.warning("Error: %s", r.content)
            if r.status_code == 201:
                j = json.loads(r.content)
                model.json['uid'] = j['uid']
                return model
            else:
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
    def list(clt: 'SketchFabClient'):
        req = clt.session.get(f'{API_URL}/me/collections')
        data = req.json()
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
        r = requests.get(r.headers['Location'])
        return SFCollection(r.json())

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
    def list_models(clt: 'SketchFabClient', collection: SFCollection):
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
