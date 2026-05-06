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

If you load in sample data, be sure to index for arches-search-extension:

```bash
python manage.py db_index reindex_database
```

