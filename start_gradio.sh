#!/bin/bash

source .venv/bin/activate 

echo "run nohup..."
rm logs/nohup.log
nohup python app_mrag/app_gradio_smart.py > logs/nohup.log 2>&1 &
echo "nohup kicked, check logs/nohup.log"
sleep 2 
ps -ef | grep [g]radio