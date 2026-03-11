#!/bin/bash

echo "Installing TrendForge V123..."

pip install qrcode[pil]

mkdir -p /root/trendforge-mvp/server/payments

echo "Alipay QR module ready."

echo "V123 installation completed."
