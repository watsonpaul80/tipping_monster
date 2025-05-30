#!/bin/bash
cd /home/ec2-user/tipping-monster
source .venv/bin/activate
# Clean up old model artifacts
echo "[INFO] Cleaning old models..." >> /home/ec2-user/tipping-monster/logs/train.log
rm -f /home/ec2-user/tipping-monster/models/model-*.json
rm -f /home/ec2-user/tipping-monster/models/model-*.bst
rm -f /home/ec2-user/tipping-monster/models/model-*.tar.gz

python train_model_v6.py >> logs/train_$(date +\%F).log 2>&1

