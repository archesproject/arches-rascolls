# RaSColls

## Reference and Sample Collections

To run RaSColls for development, clone the repository and cd to the project directory and run:

```bash
pip install -e .
```

After installation, load the RaSColls models and reference data:

```bash
python manage.py packages -o load_package -a arches_rascolls -db -y -dev
```

```bash
python manage.py report_configs load
```

To import resource data from a directory of `.xlsx` files and rebuild descriptors, search index, and report configs:

```bash
python manage.py load_rascolls_data <path-to-data-pkg>
```

Use `--format branch-excel` for branch-excel formatted files (default is `tile-excel`):

```bash
python manage.py load_rascolls_data <path-to-data-pkg> --format branch-excel
```

If you load in sample data, be sure to index for arches-search-extension:

```bash
python manage.py arches_search reindex_database
```

## Featured search items

The Featured Items tab on the search landing page is populated from the `FeaturedSearchItem` model, which is edited in the Django admin. Each item points at a saved search. The picker only lists saved searches whose creator has Django's "Staff status" (`is_staff`) flag set, so a search saved by an ordinary user cannot be featured. On save the linked search also has to have `terms` or `groups` in its query definition, otherwise the form rejects it as not a runnable query.

`presentation` is a JSON object that controls how the card is drawn:

```json
{
    "icon": "pi-palette",
    "color": "#0d9488",
    "label": "Pigments and Colourants",
    "description": "Reference pigments, dyes, and colourant samples."
}
```

`icon` and `color` are required and are validated on save. `icon` is a bare PrimeIcons suffix (`pi-palette`, not `pi pi-palette`) and sets the glyph on the card. `color` is a `#rrggbb` hex value and sets the background of the tile behind the glyph.

`label` and `description` are optional. If you leave them out the card falls back to the name and description of the saved search. Any other keys are ignored.
