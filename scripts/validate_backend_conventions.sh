#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_ROOT="${REPO_ROOT}/backend"

if [[ ! -d "${BACKEND_ROOT}" ]]; then
  echo "ERROR: Backend-Verzeichnis nicht gefunden: ${BACKEND_ROOT}"
  exit 1
fi

errors=0

print_error() {
  echo "ERROR: $1"
  errors=$((errors + 1))
}

print_info() {
  echo "INFO: $1"
}

find_backend_files() {
  local name="$1"
  find "${BACKEND_ROOT}" \
    \( -type d \
      \( -name ".git" -o -name ".idea" -o -name ".mypy_cache" -o -name ".pytest_cache" \
         -o -name ".ruff_cache" -o -name ".tox" -o -name "dist" -o -name "build" \
         -o -name ".next" -o -name ".cache" -o -name "node_modules" -o -name "__pycache__" \
         -o -name ".venv" -o -name "venv" -o -name "env" -o -name "site-packages" \) \
    \) -prune -o -type f -name "${name}" -print 2>/dev/null
}

check_forbidden_filenames() {
  local forbidden=(
    "model.py"
    "models.py"
    "service.py"
    "services.py"
    "serializer.py"
    "serializers.py"
    "view.py"
    "views.py"
    "permission.py"
    "permissions.py"
    "admin.py"
  )

  for name in "${forbidden[@]}"; do
    while IFS= read -r path; do
      [[ -z "${path}" ]] && continue
      print_error "Verbotener Dateiname gefunden: ${path#${REPO_ROOT}/}"
    done < <(find_backend_files "${name}" || true)
  done
}

discover_django_apps() {
  mapfile -t APPS < <(
    find "${BACKEND_ROOT}" -mindepth 2 -maxdepth 2 -type f -name "apps.py" \
      -printf "%h\n" 2>/dev/null | sort -u
  )
}

check_required_structure_for_app() {
  local app_dir="$1"
  local app_rel="${app_dir#${REPO_ROOT}/}"
  local required_dirs=(
    "admin"
    "models"
    "api"
    "api/v1"
    "api/v1/services"
    "api/v1/views"
    "api/v1/serializers"
    "api/v1/permissions"
    "api/v1/schema"
  )

  for rel in "${required_dirs[@]}"; do
    local dir_path="${app_dir}/${rel}"
    if [[ ! -d "${dir_path}" ]]; then
      print_error "${app_rel}: Pflichtverzeichnis fehlt: ${rel}"
      continue
    fi

    if [[ ! -f "${dir_path}/__init__.py" ]]; then
      print_error "${app_rel}: __init__.py fehlt in ${rel}"
    fi
  done
}

check_init_files_no_logic() {
  local app_dir="$1"
  while IFS= read -r init_file; do
    [[ -z "${init_file}" ]] && continue
    if grep -nE '^[[:space:]]*(class|def)[[:space:]]+' "${init_file}" >/dev/null; then
      print_error "__init__.py mit Logik gefunden: ${init_file#${REPO_ROOT}/}"
    fi
  done < <(find "${app_dir}" -type f -name "__init__.py" 2>/dev/null || true)
}

check_layer_naming() {
  local app_dir="$1"
  local app_rel="${app_dir#${REPO_ROOT}/}"

  check_layer_files "${app_dir}/admin" "${app_rel}" "admin" ".*\\.py$"
  check_layer_files "${app_dir}/models" "${app_rel}" "models" ".*\\.py$"
  check_layer_files "${app_dir}/api/v1/serializers" "${app_rel}" "serializers" "^[a-z0-9_]+\\.py$"
  check_layer_files "${app_dir}/api/v1/views" "${app_rel}" "views" "^[a-z0-9_]+\\.py$"
  check_layer_files "${app_dir}/api/v1/permissions" "${app_rel}" "permissions" "^[a-z0-9_]+\\.py$"
  check_layer_files "${app_dir}/api/v1/schema" "${app_rel}" "schema" "^[a-z0-9_]+\\.py$"
  check_layer_files "${app_dir}/api/v1/services" "${app_rel}" "services" "^[a-z0-9_]+_service\\.py$"
}

check_layer_files() {
  local dir_path="$1"
  local app_rel="$2"
  local layer_name="$3"
  local pattern="$4"

  [[ ! -d "${dir_path}" ]] && return 0

  while IFS= read -r file_path; do
    [[ -z "${file_path}" ]] && continue
    local base
    base="$(basename "${file_path}")"
    [[ "${base}" == "__init__.py" ]] && continue

    if [[ ! "${base}" =~ ${pattern} ]]; then
      print_error "${app_rel}: ungueltiger Dateiname in ${layer_name}: ${base}"
    fi
  done < <(find "${dir_path}" -maxdepth 1 -type f -name "*.py" 2>/dev/null || true)
}

main() {
  print_info "Pruefe Backend-Struktur und Naming-Conventions..."

  check_forbidden_filenames
  discover_django_apps

  if [[ "${#APPS[@]}" -eq 0 ]]; then
    print_info "Keine Django-App mit apps.py unter backend/* erkannt. Strukturpruefung uebersprungen."
  fi

  for app in "${APPS[@]}"; do
    print_info "Pruefe App: ${app#${REPO_ROOT}/}"
    check_required_structure_for_app "${app}"
    check_init_files_no_logic "${app}"
    check_layer_naming "${app}"
  done

  if [[ "${errors}" -gt 0 ]]; then
    echo "ERROR: Backend-Konventionspruefung fehlgeschlagen (${errors} Fehler)."
    exit 1
  fi

  echo "OK: Backend-Konventionspruefung erfolgreich."
}

main "$@"
