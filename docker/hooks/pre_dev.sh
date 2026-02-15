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
    cd "$pkg_dir"
    pkg_name=$(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d.get('project',{}).get('name',''))" 2>/dev/null)
    if [ -n "$pkg_name" ]; then
        pip uninstall -y "$pkg_name" 2>/dev/null || true
    fi
    pip install --no-deps -e .
done

echo ""
echo "----- *** RUNNING REPORT CONFIG LOAD *** -----"
echo ""

cd ${APP_ROOT}
${WEB_ROOT}/ENV/bin/python manage.py report_configs load