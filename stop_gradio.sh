#!/bin/bash

# 捕获 TERM 信号，防止意外终止
trap '' TERM

pgrep -f app_mrag/app_gradio | xargs -r kill
pkill -9 -f MultiModal_Rag/venv/lib/python3.10/site-packages/gradio/frpc_linux_amd64_v0.2
pkill -9 -f MultiModal_Rag/venv/lib/python3.12/site-packages/gradio/frpc_darwin_amd64_v0.2
pkill -9 -f MultiModal_Rag/venv/lib/python3.10/site-packages/gradio/frpc_darwin_amd64_v0.2
#pgrep -f gradio | xargs -r kill

sleep 2

ps -ef | grep [g]radio

# 恢复默认的 TERM 信号处理
trap - TERM
