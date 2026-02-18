#!/bin/bash
# Install mounted sibling packages in editable mode for development.
# This hook is called by entrypoint.sh before starting the dev server.
#
# Scans ${WEB_ROOT} for any directory containing a pyproject.toml and
# installs it editable. Skips the current project (handled by the
# entrypoint's own pip install -e).
#
# --no-deps is used because all dependencies are already compiled in
# the image's venv — we only need to swap in the live source code.

source ${WEB_ROOT}/ENV/bin/activate

for toml in ${WEB_ROOT}/*/pyproject.toml; do
    pkg_dir=$(dirname "$toml")
    [ "$pkg_dir" = "${APP_ROOT}" ] && continue
    echo "Installing editable: $(basename $pkg_dir)"
    cd "$pkg_dir" && pip install --no-deps -e .
done

cd ${APP_ROOT}
