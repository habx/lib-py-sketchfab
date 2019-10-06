# Sketchfab API Client

## Getting started
Install the module:
```sh
pip3 install sketchfab
```
This code creates a directory for each of your collection and places all models inside it.
```python
import os
import sketchfab

sfc = sketchfab.Client('YOUR-API-KEY')
for c in sfc.collections():
    print("Collection:", c)
    col_dir = os.path.join("download", c.name)
    os.makedirs(col_dir, exist_ok=True)
    for m in c.models():
        model_dir = os.path.join(col_dir, m.name)
        print(f"  Model: {m.name} ({model_dir})")
        if not os.path.exists(model_dir):
            os.rename(m.download_to_dir(), model_dir)
```
Which will give you something like that:
```text
Collection: Collection{empty collection}
Collection: Collection{housing-updates}
  Model: tableKitchen80x200 (download/housing-updates/tableKitchen80x200)
  Model: kitchenModSink120x65x210 (download/housing-updates/kitchenModSink120x65x210)
  Model: kitchenModSink60x65x90 (download/housing-updates/kitchenModSink60x65x90)
  Model: kitchenModFridge60x65x210 (download/housing-updates/kitchenModFridge60x65x210)
  Model: kitchenModCorner65x65x210 (download/housing-updates/kitchenModCorner65x65x210)
  Model: kitchenModBasic10x65x90 (download/housing-updates/kitchenModBasic10x65x90)
  Model: kitchenModWasher60x65x210 (download/housing-updates/kitchenModWasher60x65x210)
  Model: kitchenModSink60x65x210 (download/housing-updates/kitchenModSink60x65x210)
  Model: kitchenModBasic20x65x210 (download/housing-updates/kitchenModBasic20x65x210)
  Model: washbasin120x60 (download/housing-updates/washbasin120x60)
  Model: kitchenModWasher60x65x90 (download/housing-updates/kitchenModWasher60x65x90)
  Model: bedDouble140x200-2 (download/housing-updates/bedDouble140x200-2)
  Model: simpleBed90x200 (download/housing-updates/simpleBed90x200)
  Model: wcFloor70x40 (download/housing-updates/wcFloor70x40)
  Model: kitchenModBasic60x65x90 (download/housing-updates/kitchenModBasic60x65x90)
  Model: kitchenModDishWasher60x65x90 (download/housing-updates/kitchenModDishWasher60x65x90)
  Model: kitchenModSink120x65x90 (download/housing-updates/kitchenModSink120x65x90)
  Model: kitchenModStove60x65x210 (download/housing-updates/kitchenModStove60x65x210)
  Model: kitchenModStove60x65x90 (download/housing-updates/kitchenModStove60x65x90)
  Model: washbasin60x60 (download/housing-updates/washbasin60x60)
  Model: tableKitchen80x140 (download/housing-updates/tableKitchen80x140)
  Model: shower90x90 (download/housing-updates/shower90x90)
  Model: kitchenModDishWasher60x65x210 (download/housing-updates/kitchenModDishWasher60x65x210)
  Model: kitchenModBasic10x65x210 (download/housing-updates/kitchenModBasic10x65x210)

```

## Why
- I couldn't find one
- The [sample codes from the sketchfab website](https://sketchfab.com/developers/data-api/v3/python) are pretty much unuseable

## Choices
- The API is designed to be as simple as possible to use

## Known issues
- The code might not be the most elegant. I'm definitely interested by any feedback you can provide me on that.
- The official swagger-based documentation is not respecting the API behavior. As such you might find that:
  - The library enforces some strange rules (like passing a model when creating a model)
  - The library doesn't properly use the API (like listing the models of a collection through search)

  In both case it was by trial and error that I discovered how to use the API. If you find better ways to do
  it I'm interested.
- The listing doesn't work with long lists (it needs to be re-implemented as an iterable calling the listing API)
- The CLI is pretty much useless at this stage

## Missing APIs
You can submit pull-requests or ask me to implement any feature that you need and might be missing.

