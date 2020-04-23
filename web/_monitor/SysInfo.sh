#!/bin/bash


echo "----------SYstem Information---------"

echo $0
echo $1
echo $$
echo "Number of Arguments", $#

while true 
do
  free -m >> /www/web/_include/MemoSysLog.text
  top -n 1 -b | head -n 1 >> /www/web/_include/CPUSysLog.text
  sleep 5m
done

