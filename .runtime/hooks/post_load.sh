#!/bin/bash
# Rascolls post-load hook: fetch private data and import via ETL

set -euo pipefail

IMPORT_ERRORS=0

run_import() {
	local file="$1"
	local name
	name=$(basename "$file" .xlsx)

	echo "--------------------------------------------"
	echo "[import] Starting: $name"
	echo "[import] File: $file"

	if [ ! -f "$file" ]; then
		echo "[import] ERROR: File not found: $file"
		IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
		return 1
	fi

	local output
	if output=$(${WEB_ROOT}/ENV/bin/python manage.py etl tile-excel-importer -s "$file" 2>&1); then
		echo "[import] SUCCESS: $name"
	else
		local exit_code=$?
		echo "[import] FAILED: $name (exit code: $exit_code)"
		IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
	fi
	echo "$output"
	echo "--------------------------------------------"
}

if [ "$FETCH_PRIVATE_DATA" = "true" ]; then
	echo "[post_load] Fetching secret from AWS Secrets Manager..."

	GITHUB_TOKEN=$(aws secretsmanager get-secret-value \
		--secret-id "ci/rascolls/load" \
		--query "SecretString" \
		--output text | jq -r '.github' 2>/dev/null || true)

	if command -v apk &>/dev/null; then apk add git; fi

	echo "[post_load] Cloning private repository..."
	if [ -n "$GITHUB_TOKEN" ]; then
		echo "[post_load] Using token-based auth"
		git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/archesproject/rascolls-data-pkg.git" /tmp/rascolls-data-pkg
	else
		echo "[post_load] WARNING: No GitHub token found, falling back to SSH"
		if command -v apk &>/dev/null; then apk add openssh-client; fi
		git clone "git@github.com:archesproject/rascolls-data-pkg.git" /tmp/rascolls-data-pkg
	fi

	echo "[post_load] Repository contents:"
	ls -la /tmp/rascolls-data-pkg/

	echo "[post_load] Starting tile-excel imports..."

	run_import /tmp/rascolls-data-pkg/Reference_and_Sample_Collection_Item.xlsx
	run_import /tmp/rascolls-data-pkg/Place.xlsx
	run_import /tmp/rascolls-data-pkg/Person.xlsx
	run_import /tmp/rascolls-data-pkg/Group.xlsx
	run_import /tmp/rascolls-data-pkg/Collection_or_Set.xlsx
	${WEB_ROOT}/ENV/bin/python manage.py report_configs load

	echo "============================================"
	if [ "$IMPORT_ERRORS" -gt 0 ]; then
		echo "[post_load] COMPLETED WITH $IMPORT_ERRORS ERROR(S)"
		exit 1
	else
		echo "[post_load] ALL IMPORTS COMPLETED SUCCESSFULLY"
	fi
	echo "============================================"
fi
