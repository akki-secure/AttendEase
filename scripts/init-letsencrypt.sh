#!/bin/bash
# 初回のみ実行するLet's Encrypt証明書取得スクリプト。
# 使い方: DOMAIN=xxx.duckdns.org ./scripts/init-letsencrypt.sh
set -e

if [ -z "$DOMAIN" ]; then
  echo "DOMAIN環境変数を指定してください（例: DOMAIN=attendease.duckdns.org ./scripts/init-letsencrypt.sh）"
  exit 1
fi

COMPOSE="docker compose -f docker-compose.prod.yml"
VOLUME="attendease_certbot_conf"

echo "### ダミー証明書を作成してnginxを起動できるようにする ###"
docker run --rm -v "$VOLUME:/etc/letsencrypt" alpine/openssl sh -c "
  mkdir -p /etc/letsencrypt/live/$DOMAIN && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/$DOMAIN/privkey.pem \
    -out /etc/letsencrypt/live/$DOMAIN/fullchain.pem \
    -subj /CN=$DOMAIN
"

echo "### nginxを起動 ###"
$COMPOSE up -d nginx

echo "### ダミー証明書を削除 ###"
docker run --rm -v "$VOLUME:/etc/letsencrypt" alpine rm -rf "/etc/letsencrypt/live/$DOMAIN"

echo "### 本番証明書を取得 ###"
$COMPOSE run --rm certbot certonly --webroot -w /var/www/certbot \
  -d "$DOMAIN" \
  --register-unsafely-without-email \
  --agree-tos --no-eff-email --force-renewal

echo "### nginxをリロード ###"
$COMPOSE exec nginx nginx -s reload

echo "完了しました。https://$DOMAIN/ で確認してください。"
