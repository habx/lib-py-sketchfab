import unittest

from sketchfab.clt import SFClient


class SketchFabTest(unittest.TestCase):
    @staticmethod
    def test_basic_stuff():
        client = SFClient()
        models = client.models(published=True)

        if models:
            model = models[0]
            # List your collections, create one if you don't have any
            collection_name = 'test collection'
            collection = client.get_collection(collection_name)
            if not collection:
                collection = client.create_collection(collection_name, [model])
            print('Model:', model.viewer_url)
            assert model.comment('All good !')
            assert collection.add_model(model)
            assert collection.remove_model(model)
            assert collection.remove_model(model)

    @staticmethod
    def test_download():
        client = SFClient()
        models = client.models()
        if models:
            model = models[0]
            tmp = model.download_to_dir()
            print('Download:', tmp)

    @staticmethod
    def test_listing_collection_models():
        clt = SFClient()
        coll_models = clt.get_collection('housing-models')
        models = coll_models.models()
        assert len(models) > 0

    @staticmethod
    def test_download_updates():
        clt = SFClient()
        coll_updates = clt.get_collection('housing-updates')
        coll_models = clt.get_collection('housing-models')
        if not coll_updates or not coll_models:
            print("Some collections are missing !")
            return

        coll_updates_models = coll_updates.models()

        for m in coll_updates_models:
            d = m.download_to_dir()
            print(f"Downloaded {m.name} to {d}")
            coll_models.add_model(m)
            coll_updates.remove_model(m)
            m.comment("Downloaded !")
