#!/bin/bash
#Data		:2018-10-08
#Author		:szj
#Function	:从本地多级目录文件中记录文件大小的脚本,取完后如目录结构和文件数量大小正确则删除该多级目录，用于光闸稳定性目的端记录收到的多级目录文件
#Version	:v1.1
#Update		:
#------------------------------------------------------------
# $1 ftp目的端待统计目录，例如/hddraid/hddftp/hddftp1
# $2 日志文件位置及文件名,例如/hddraid/hddftp/stability/dest/logs/task4.log"
# $3 文件夹文件数量"
# $4 每次执行间隔
# $5 统计多长时间以前的文件夹，避免大量文件未传输完成就统计，单位分钟
# $6 文件夹大小,du -b
# 请在dest目录下执行
#------------------------------------------------------------
if [ $# -ne "6" ]
then
   echo "参数数量不正确"
   exit 0
fi 
i=1
myFolder=$1
myLog=$2
flag=fgapfile
file_num=$3
sleep_time=$4
file_time=$5
filesize=$6
rm -rf $myLog*
if [ ! -d "$myFolder" ]
then  
　　echo "$myFolder 不存在,结束脚本"
exit 0 
fi
while [ true ]
do
	for file in `find $myFolder/ -mindepth 1 -maxdepth 1 -type d -cmin +$file_time`
	do	
		filesize_tmp=`du -b $file |grep $file$ |awk '{print $1}'`
		if [ $filesize -eq $filesize_tmp ]
		then
			filenum=`find $file/ -cmin +$file_time ! -name "*.sutmp" ! -name "*.SUTMP" ! -name "*.0000*" -type f |wc -l`
			if [ $filenum -eq $file_num ]
			then
				echo $file >> $myLog$i
				FILE_SIZE=`ls -l  $myLog$i| awk '{print $5}'`
				if [ ${FILE_SIZE} -gt 10485760 ]
				then 
					let i=`expr $i+1` 
				fi
				rm -rf $file
				while [ -d "$file" ]
				do
					rm -rf $file
					sleep 1
				done
			fi
		fi
	done
	sleep $sleep_time
done

