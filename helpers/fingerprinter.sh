#!/usr/bin/env bash

OUTPUT_FILE="gitlab_css_versions.txt"
ASSET_DIR="/opt/gitlab/embedded/service/gitlab-rails/public/assets"
TAGS_API="https://registry.hub.docker.com/v2/repositories/gitlab/gitlab-ce/tags?page_size=100"
NUM_TAGS=5  # Limit to the most recent 20 tags

# Clear output file
> "$OUTPUT_FILE"

echo "[*] Fetching latest GitLab CE tags from Docker Hub..."

TAGS=$(curl -s "$TAGS_API" | jq -r '.results[].name' | head -n "$NUM_TAGS")

if [[ -z "$TAGS" ]]; then
    echo "[!] Failed to fetch tags. Exiting."
    exit 1
fi

for TAG in $TAGS; do
    echo "[*] Processing tag: $TAG"

    echo "  [+] Pulling gitlab/gitlab-ce:$TAG..."
    if ! docker pull gitlab/gitlab-ce:"$TAG" > /dev/null 2>&1; then
        echo "  [!] Failed to pull image: $TAG"
        continue
    fi

    echo "  [+] Extracting CSS filename..."
    CSS_FILE=$(docker run --rm --entrypoint "" gitlab/gitlab-ce:"$TAG" \
        ls "$ASSET_DIR" 2>/dev/null | grep -E '^application-.*\.css$' | grep -v '\.gz' | head -n1)

    if [[ -n "$CSS_FILE" ]]; then
        echo "  [+] Found CSS: $CSS_FILE"
        echo "\"$CSS_FILE\":\"$TAG\"," >> "$OUTPUT_FILE"
    else
        echo "  [-] No matching CSS found"
    fi

    echo "  [-] Removing image gitlab/gitlab-ce:$TAG"
    docker rmi gitlab/gitlab-ce:"$TAG" > /dev/null 2>&1

    echo ""
done

echo "[✓] Done. Output saved to $OUTPUT_FILE"
