#!/bin/bash
# ============================================================
# KCK — First-time Hetzner server setup
# Run this ONCE on a fresh Ubuntu 22.04+ Hetzner VPS
#
# Usage: ssh root@YOUR_IP 'bash -s' < scripts/setup-hetzner.sh
# ============================================================

set -euo pipefail

DOMAIN="${1:-kenyakorea.com}"
EMAIL="${2:-admin@kenyakorea.com}"
APP_DIR="/opt/kck/backend"

echo "=== KCK Server Setup ==="
echo "Domain: $DOMAIN"
echo "Email:  $EMAIL"
echo ""

# ─── 1. System packages ───────────────────────────────
echo "[1/7] Installing system packages..."
apt-get update -qq
apt-get install -y -qq docker.io docker-compose-v2 git curl ufw fail2ban

systemctl enable --now docker

# ─── 2. Firewall ──────────────────────────────────────
echo "[2/7] Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# ─── 3. Create deploy user ────────────────────────────
echo "[3/7] Creating deploy user..."
if ! id -u deploy &>/dev/null; then
    useradd -m -s /bin/bash -G docker deploy
    mkdir -p /home/deploy/.ssh
    cp /root/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
    chown -R deploy:deploy /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    chmod 600 /home/deploy/.ssh/authorized_keys 2>/dev/null || true
    echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose" >> /etc/sudoers.d/deploy
fi

# ─── 4. Clone repo ────────────────────────────────────
echo "[4/7] Setting up application..."
mkdir -p "$APP_DIR"
chown deploy:deploy "$APP_DIR"

if [ ! -d "$APP_DIR/.git" ]; then
    echo "  Clone your repo: git clone YOUR_REPO_URL $APP_DIR"
    echo "  Then copy .env.example to .env and fill in values"
else
    echo "  Repo already exists at $APP_DIR"
fi

# ─── 5. Create .env template ──────────────────────────
echo "[5/7] Creating .env template..."
if [ ! -f "$APP_DIR/.env" ]; then
    cat > "$APP_DIR/.env" << 'ENVEOF'
# ─── Database ──────────────────────────────────
DB_NAME=kck
DB_USER=kck
DB_PASSWORD=CHANGE_ME_STRONG_PASSWORD_HERE

# ─── Django ────────────────────────────────────
DJANGO_SECRET_KEY=CHANGE_ME_GENERATE_WITH_python3_-c_"from_django.core.management.utils_import_get_random_secret_key;print(get_random_secret_key())"
DJANGO_ALLOWED_HOSTS=kenyakorea.com,www.kenyakorea.com
CORS_ALLOWED_ORIGINS=https://kenyakorea.com,https://www.kenyakorea.com
KCK_BASE_URL=https://kenyakorea.com

# ─── Laravel ───────────────────────────────────
APP_KEY=base64:GENERATE_WITH_php_artisan_key:generate
APP_ENV=production
APP_DEBUG=false

# ─── Email ─────────────────────────────────────
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=KCK <noreply@kenyakorea.com>

# ─── Optional ──────────────────────────────────
SENTRY_DSN=
ENVEOF
    echo "  Created $APP_DIR/.env — EDIT IT with real values!"
fi

# ─── 6. SSL with Let's Encrypt ────────────────────────
echo "[6/7] SSL setup..."
echo "  After first deploy, run:"
echo "  docker compose run --rm certbot certonly --webroot -w /var/lib/letsencrypt -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos"
echo "  Then: docker compose restart nginx"

# ─── 7. Summary ───────────────────────────────────────
echo ""
echo "[7/7] Setup complete!"
echo ""
echo "=== Next steps ==="
echo "1. Clone your repo:  cd $APP_DIR && git clone YOUR_REPO $APP_DIR"
echo "2. Edit .env:        nano $APP_DIR/.env"
echo "3. First deploy:     cd $APP_DIR && docker compose up -d"
echo "4. Run migrations:   docker compose run --rm backend python manage.py migrate"
echo "5. Create superuser: docker compose run --rm backend python manage.py createsuperuser"
echo "6. Setup SSL:        (see step 6 above)"
echo ""
echo "=== GitHub Secrets needed ==="
echo "  HETZNER_HOST     = $(curl -s ifconfig.me)"
echo "  HETZNER_USER     = deploy"
echo "  HETZNER_SSH_KEY  = (your private SSH key)"
echo ""
