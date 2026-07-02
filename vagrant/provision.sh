#!/usr/bin/env bash
set -euo pipefail

echo "[provision] Installing Docker + Docker Compose..."
apt-get update -qq
apt-get install -y -qq docker.io docker-compose-v2
usermod -aG docker vagrant

echo "[provision] Building service images..."
cd /home/vagrant/ticketforge

docker compose -f docker-compose.yml up -d --wait

DOCKER_BUILDKIT=1 docker compose -f docker-compose.prod.yml build

echo "[provision] Starting full stack..."
docker compose -f docker-compose.prod.yml up -d

echo "[provision] Done. Services will be available after a few seconds."
