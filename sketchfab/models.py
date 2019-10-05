"""
Sketchfab models
"""
from typing import Dict, Any, List


class SFModel:
    """
    [3D Model](https://docs.sketchfab.com/data-api/v3/index.html#/models)
    """

    def __init__(self, j: Dict[str, Any] = None, clt: 'SketchFabClient' = None):
        self.json = j if j else {}
        self.clt = clt

    @property
    def name(self) -> str:
        """name of the model"""
        return self.json.get('name')

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

    def __str__(self) -> str:
        return f'Model{{{self.name}}}'


class SFCollection:
    """
    [Collection of models](https://docs.sketchfab.com/data-api/v3/index.html#/collections)
    """

    def __init__(self, j: Dict[str, Any] = None, clt: 'SketchFabClient' = None):
        self.json = j if j else {}
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

    def __str__(self) -> str:
        return f'Collection{{{self.name}}}'
