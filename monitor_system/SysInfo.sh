#!/bin/bash


echo "----------SYstem Information---------"

echo $0
echo $1
echo $$
echo "Number of Arguments", $#

while true 
do
  free -m >> /www/Lora_Pro/monitor/MemoSysLog.text
  date >> /www/Lora_Pro/monitor/MemoSysLog.text
  top -n 1 -b | head -n 1 >> /www/Lora_Pro/monitor/CPUSysLog.text
  date >> /www/Lora_Pro/monitor/CPUSysLog.text
  sleep 5m
done

