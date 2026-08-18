ubuntu@<your-vm-ip>   # SSH as your Oracle Cloud user (often ubuntu)

# 1. Set your secrets (paste your real values)
export GROQ_API_KEY="gsk_..."
export TELEGRAM_BOT_TOKEN="8856755792:..."
export SPREADSHEET_ID="1LyhcYroyweyqjVRObVemg8sYePhHonmZn9MLpE9vY9g"
export GOOGLE_CREDENTIALS_JSON='{"installed":{...}}'   # contents of credentials.json
export GOOGLE_TOKEN_JSON='{"token": "...", ...}'        # contents of token.json

# 2. Run the setup script (from the repo on GitHub)
curl -sL https://raw.githubusercontent.com/Gongwasubash/jobpalner/master/deploy/setup_vps.sh -o setup.sh
chmod +x setup.sh
./setup.sh

# 3. Done. Check logs
journalctl -u ideaexecuter -f