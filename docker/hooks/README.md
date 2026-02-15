# Docker Hooks

Hook scripts are sourced by the entrypoint at specific points in the container lifecycle.
Place `.sh` files here named after the hook you want to implement.

All hooks run with the virtualenv already activated and `APP_ROOT` as the working directory.

---

## Available Hooks

### `pre_dev.sh`

Runs before the Django development server starts (`run_dev_server`).

Use this to install editable sibling packages, set up local tooling, or any other
dev-only setup that should happen each time the container starts.

Example — install mounted sibling packages in editable mode:

```bash
#!/bin/bash
source ${WEB_ROOT}/ENV/bin/activate

for toml in ${WEB_ROOT}/*/pyproject.toml; do
    pkg_dir=$(dirname "$toml")
    [ "$pkg_dir" = "${APP_ROOT}" ] && continue
    echo "Installing editable: $(basename $pkg_dir)"
    cd "$pkg_dir" && pip install --no-deps -e .
done

cd ${APP_ROOT}
```

---

### `pre_start.sh`

Runs before the Gunicorn production server starts (`run_gunicorn`).

Use this for production startup tasks: running migrations, collecting static files,
warming caches, etc.

Example:

```bash
#!/bin/bash
python manage.py migrate --no-input
python manage.py collectstatic --no-input
```

---

### `post_load.sh`

Runs after `manage.py packages -o load_package` completes during `reset_database`.

Use this to load additional fixtures, import data, or run any setup that depends on
the package being loaded.

Example:

```bash
#!/bin/bash
python manage.py loaddata my_fixtures.json
```

---

### `post_reindex.sh`

Runs after `manage.py es reindex_database` completes during `reset_database`.

Use this for any final setup steps that require a fully initialized database and
search index.

Example:

```bash
#!/bin/bash
python manage.py create_admin_user
```
