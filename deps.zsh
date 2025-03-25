COLOR_ENV='\033[1;34m'
COLOR_INFO='\033[1;36m'
COLOR_ERROR='\033[1;31m'
NC='\033[0m'
for env in $(conda env list | awk '{print $1}' | grep -v '^#' | grep -v '^$' | grep -v '^base$'); do
    echo -e "${COLOR_INFO}Updating dependencies in ${COLOR_ENV}$env${NC}"
    conda update --all -n "$env" -y || echo -e "${COLOR_ERROR}Update failed for ${COLOR_ENV}$env${NC}"
done
