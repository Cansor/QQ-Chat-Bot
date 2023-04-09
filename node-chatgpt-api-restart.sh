#!/bin/bash
# 这是一个模板，需要自行根据自己的环境修改路径之类的东西

cd /home/Cansor/qq_bot/node-chatgpt-api
pid=`sudo netstat -anp | grep 3000 | awk -F "/" '(NR<=1){print $1}' | awk '(NR<=1){print $7}'`
if [ "$pid" == "" ]
then
    echo "pid is empty"
else
    kill -9 $pid
    echo "killing..."
    sleep 3
fi
echo "starting..."
nohup npm start >./bing-api-server.log 2>&1 &
echo "ok!"
