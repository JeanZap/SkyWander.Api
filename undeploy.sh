#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-skywander-api}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${APP_DIR:-$SCRIPT_DIR}"
REMOVE_VENV="${REMOVE_VENV:-false}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Execute com sudo: sudo bash undeploy.sh"
  exit 1
fi

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "==> Parando e desabilitando servico ${SERVICE_NAME}"
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}\.service"; then
  systemctl disable --now "${SERVICE_NAME}" || true
fi

if [[ -f "$SERVICE_FILE" ]]; then
  echo "==> Removendo arquivo do servico: $SERVICE_FILE"
  rm -f "$SERVICE_FILE"
fi

echo "==> Recarregando systemd"
systemctl daemon-reload

if [[ -f "$APP_DIR/wsgi.py" ]]; then
  echo "==> Removendo wsgi.py gerado no deploy"
  rm -f "$APP_DIR/wsgi.py"
fi

if [[ "${REMOVE_VENV}" == "true" && -d "$APP_DIR/.venv" ]]; then
  echo "==> Removendo virtualenv em $APP_DIR/.venv"
  rm -rf "$APP_DIR/.venv"
fi

echo "==> Undeploy concluido"
echo "Dica: para remover o venv tambem, use REMOVE_VENV=true."
