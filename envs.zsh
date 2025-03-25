TARGET_VERSION=3.13.2
COLOR_ENV='\033[1;34m'
COLOR_CURR='\033[1;33m'
COLOR_TARGET='\033[1;32m'
COLOR_INFO='\033[1;36m'
COLOR_ERROR='\033[1;31m'
NC='\033[0m'
for env in $(conda env list | awk '{print $1}' | grep -v '^#' | grep -v '^$' | grep -v '^base$'); do
    current=$(conda run -n "$env" python --version 2>/dev/null | awk '{print $2}')
    if [[ -z "$current" ]]; then
        echo -e "${COLOR_INFO}No Python in ${COLOR_ENV}$env${NC}"
        continue
    fi
    if [[ "$current" != "$TARGET_VERSION" ]]; then
        echo -e "${COLOR_ENV}$env${NC}: ${COLOR_CURR}$current${NC} → ${COLOR_TARGET}$TARGET_VERSION${NC} (Upgrading)"
        conda install -n "$env" python=$TARGET_VERSION --update-deps -y || echo -e "${COLOR_ERROR}Upgrade failed for ${COLOR_ENV}$env${NC}"
    else
        echo -e "${COLOR_ENV}$env${NC}: Already at ${COLOR_TARGET}$TARGET_VERSION${NC}"
    fi
done
