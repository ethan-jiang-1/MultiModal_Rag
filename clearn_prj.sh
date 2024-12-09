#!/bin/bash

# 查找当前目录及其子目录下所有的__pycache__目录并删除
find . -type d -name '__pycache__' -exec rm -rf {} +

