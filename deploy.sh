#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-skywander-api}"
PORT="${PORT:-5000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${APP_DIR:-$SCRIPT_DIR}"

if [[ ! -f "$APP_DIR/main.py" ]]; then
  echo "Erro: main.py nao encontrado em APP_DIR=$APP_DIR"
  exit 1
fi

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Execute com sudo: sudo bash deploy.sh"
  exit 1
fi

APP_USER="${APP_USER:-${SUDO_USER:-pi}}"
if ! id -u "$APP_USER" >/dev/null 2>&1; then
  echo "Erro: usuario APP_USER=$APP_USER nao existe."
  exit 1
fi

echo "==> Instalando dependencias do sistema"
apt update
apt install -y python3-venv python3-pip python3-dev build-essential

echo "==> Criando/atualizando virtualenv"
if [[ ! -d "$APP_DIR/.venv" ]]; then
  sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
fi

echo "==> Instalando dependencias Python"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" -m pip install --upgrade pip setuptools wheel
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install gunicorn

echo "==> Gerando wsgi.py"
cat > "$APP_DIR/wsgi.py" <<'PY'
from main import app
PY
chown "$APP_USER":"$APP_USER" "$APP_DIR/wsgi.py"

if [[ ! -f "$APP_DIR/.env" ]]; then
  echo "Aviso: arquivo .env nao encontrado em $APP_DIR/.env"
  echo "Crie-o antes de usar os GPIOs."
fi

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
echo "==> Criando servico systemd em $SERVICE_FILE"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=SkyWander API
After=network.target

[Service]
User=${APP_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=${APP_DIR}/.venv/bin/gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 wsgi:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "==> Ativando servico"
systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

echo "==> Deploy concluido"
echo "Status do servico:"
systemctl --no-pager --full status "${SERVICE_NAME}" || true
