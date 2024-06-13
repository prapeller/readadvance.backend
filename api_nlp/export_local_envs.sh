#!/bin/bash

ENV_FILES=(
    "./.envs/.local/.api_nlp"
)

# export variables from a single .env file
export_vars_from_file() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        while IFS='=' read -r key value
        do
            # Trim spaces and export non-empty, non-commented lines
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            if [ ! -z "$key" ] && [[ ! $key =~ ^# ]]; then
                export "$key=$value"
            fi
        done < "$file_path"
    else
        echo "Environment file not found: $file_path"
    fi
}

# Loop over the array and export variables from each file
for env_file in "${ENV_FILES[@]}"; do
    export_vars_from_file "$env_file"
done

printenv
