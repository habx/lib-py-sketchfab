"""
Sketchfab models
"""
from typing import Dict, Any, List, Union


class SFModelOptions:
    def __init__(self, parent: 'SFModel'):
        self.parent = parent
        self.json = parent.json.get('options')
        if not self.json:
            self.json = {}

    @property
    def shading(self) -> str:
        return self.json.get('shading', 'lit')

    @shading.setter
    def shading(self, value: str):
        assert value in 'shadeless', 'lit'
        self.set_property('shading', value)

    def set_property(self, name: str, value: Any):
        self.json[name] = value
        self.parent.set_property('options', self.json)


class SFModel:
    """
    [3D Model](https://docs.sketchfab.com/data-api/v3/index.html#/models)
    """

    def __init__(self, j: Dict[str, Any] = None, clt: 'SketchFabClient' = None):
        self.json = j if j else {}
        self.modified: List[str] = []
        self.clt = clt

    def set_property(self, name: str, value: Any):
        if name not in self.modified:
            self.modified.append(name)
        self.json[name] = value

    @property
    def name(self) -> str:
        """name of the model"""
        return self.json.get('name')

    @name.setter
    def name(self, value: str):
        self.set_property('name', value)

    @property
    def description(self) -> str:
        return self.json.get('description')

    @description.setter
    def description(self, value: str):
        self.set_property('description', value)

    @property
    def tags(self) -> List[str]:
        return self.json.get('tags')

    @tags.setter
    def tags(self, value: List[str]):
        self.set_property('tags', value)

    @property
    def categories(self) -> List[str]:
        return self.json.get('categories')

    @categories.setter
    def categories(self, value: List[str]):
        self.set_property('categories', value)

    @property
    def uid(self) -> str:
        """uid of the model"""
        return self.json.get('uid')

    @property
    def viewer_url(self) -> str:
        """viewer URL (to be opened in a browser)"""
        return self.json.get('viewerUrl')

    @property
    def is_published(self) -> bool:
        return self.json.get('publishedAt') is not None

    @property
    def private(self) -> bool:
        return self.json.get('private')

    @private.setter
    def private(self, value: bool):
        self.json['private'] = value

    @property
    def options(self) -> SFModelOptions:
        return SFModelOptions(self)

    def comment(self, msg: str):
        """Add a comment to a model"""
        from sketchfab.api import SFModelsApi
        return SFModelsApi.comment(self.clt, self, msg)

    def download(self) -> str:
        """Download a model as a ZIP file and return the path of the created file"""
        from sketchfab.api import SFModelsApi
        return SFModelsApi.download(self.clt, self)

    def download_to_dir(self) -> str:
        """Download a model as a directory"""
        from sketchfab.api import SFModelsApi
        return SFModelsApi.download_to_dir(self.clt, self)

    def update(self) -> bool:
        """Update a model"""
        from sketchfab.api import SFModelsApi
        return SFModelsApi.update_model(self.clt, self)

    def __str__(self) -> str:
        return f'Model{{{self.name}}}'


class SFCollection:
    """
    [Collection of models](https://docs.sketchfab.com/data-api/v3/index.html#/collections)
    """

    def __init__(self, j: Dict[str, Any] = None, clt: 'SketchFabClient' = None):
        self.json = j if j else {}
        self.modified: List[str] = []
        self.clt = clt

    @property
    def name(self) -> str:
        """Name of the collection"""
        return self.json.get('name')

    @property
    def uid(self) -> str:
        """UID of the collection"""
        return self.json.get('uid')

    def models(self) -> List[SFModel]:
        """Fetch the models of the collection"""
        from sketchfab.api import SFCollectionsApi
        return SFCollectionsApi.list_models(self.clt, self)

    def add_model(self, model: SFModel) -> bool:
        """
        Add a model to a collection

        Parameters
        ----------
        model : SFModel
            Model to add

        Returns
        -------
        bool
            If the model could be added
        """
        from sketchfab.api import SFCollectionsApi
        return SFCollectionsApi.add_model(self.clt, self, model)

    def remove_model(self, model: SFModel) -> bool:
        """Remove a model from a collection"""
        from sketchfab.api import SFCollectionsApi
        return SFCollectionsApi.remove_model(self.clt, self, model)

    def update(self) -> bool:
        """Update the collection"""
        from sketchfab.api import SFCollectionsApi
        return SFCollectionsApi.update(self.clt, self)

    def __str__(self) -> str:
        return f'Collection{{{self.name}}}'
