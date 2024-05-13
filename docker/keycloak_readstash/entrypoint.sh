#!/bin/bash

if [ -f "/opt/keycloak/data/import/realm-export-readstash.json" ]; then
echo "Importing realm from /opt/keycloak/data/import/realm-export-readstash.json"
/opt/keycloak/bin/kc.sh import --file /opt/keycloak/data/import/realm-export-readstash.json --override false
fi

exec /opt/keycloak/bin/kc.sh "$@"
