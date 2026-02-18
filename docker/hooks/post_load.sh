#!/bin/bash
# Rascolls post-load hook: fetch private data and import via ETL

if [ "$FETCH_PRIVATE_DATA" = "true" ]; then
	echo "Fetching secret from AWS Secrets Manager..."

	GITHUB_TOKEN=$(aws secretsmanager get-secret-value \
		--secret-id "ci/rascolls/load" \
		--query "SecretString" \
		--output text | jq -r '.github')

	ADMIN_PW=$(aws secretsmanager get-secret-value \
		--secret-id "ci/rascolls/load" \
		--query "SecretString" \
		--output text | jq -r '.password')

	echo "Cloning private repository..."
	git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/archesproject/rascolls-data-pkg.git" /tmp/rascolls-data-pkg
	printf "$ADMIN_PW\n$ADMIN_PW" | ${WEB_ROOT}/ENV/bin/python manage.py changepassword admin
	${WEB_ROOT}/ENV/bin/python manage.py etl tile-excel-importer -s /tmp/rascolls-data-pkg/Reference_and_Sample_Collection_Item.xlsx
	${WEB_ROOT}/ENV/bin/python manage.py etl tile-excel-importer -s /tmp/rascolls-data-pkg/Place.xlsx
	${WEB_ROOT}/ENV/bin/python manage.py etl tile-excel-importer -s /tmp/rascolls-data-pkg/Person.xlsx
	${WEB_ROOT}/ENV/bin/python manage.py etl tile-excel-importer -s /tmp/rascolls-data-pkg/Group.xlsx
	${WEB_ROOT}/ENV/bin/python manage.py etl tile-excel-importer -s /tmp/rascolls-data-pkg/Collection_or_Set.xlsx
fi
