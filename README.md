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
