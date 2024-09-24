pkill -f "uvicorn server.main:app --reload --port 8200"
while pgrep -f "uvicorn server.main:app --reload --port 8200" > /dev/null; do
    echo "killing server..."
    sleep 1 # 每秒检查一次
done
echo "smart report server stoped"