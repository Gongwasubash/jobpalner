#!/usr/bin/env bash
set -euo pipefail

echo "==> Updating system"
sudo apt-get update -y
sudo apt-get install -y ffmpeg python3 python3-pip python3-venv git curl

APP_DIR="$HOME/ideaexecuter"
if [ ! -d "$APP_DIR" ]; then
  echo "==> Cloning repo"
  git clone https://github.com/Gongwasubash/jobpalner.git "$APP_DIR"
fi

cd "$APP_DIR"

echo "==> Creating venv"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "==> Writing .env from environment"
cat > "$APP_DIR/.env" <<EOF
GROQ_API_KEY=$GROQ_API_KEY
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
PLANS_BASE_FOLDER=./plans
SPREADSHEET_ID=$SPREADSHEET_ID
GOOGLE_CREDENTIALS_JSON=$GOOGLE_CREDENTIALS_JSON
GOOGLE_TOKEN_JSON=$GOOGLE_TOKEN_JSON
PORT=8080
EOF

echo "==> Installing systemd service"
sudo tee /etc/systemd/system/ideaexecuter.service > /dev/null <<EOF
[Unit]
Description=Idea Executer Telegram Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/bot.py
Restart=always
RestartSec=5
EnvironmentFile=$APP_DIR/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ideaexecuter
sudo systemctl restart ideaexecuter

echo "==> Status"
sleep 3
sudo systemctl status ideaexecuter --no-pager || true
echo "Done. Bot runs via: systemctl status ideaexecuter / journalctl -u ideaexecuter -f"