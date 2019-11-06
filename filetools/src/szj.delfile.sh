#!/bin/bash
#删除目的文件
#cd /hddraid/hddftp/
#rm -fr hddftp1/* hddftp2/* hddftp3/* hddftp4/* hddftp5/*
#cd /ssdraid/ssdsmb/
#rm -fr ssdsmb1/* ssdsmb/* ssdsmb3/* ssdsmb4/* ssdsmb5/*
#cd /hddraid/stability/dest
#rm -f logs/*
#cd /ssdraid/ssdnfs/
#rm -rf ssdnfs1/* ssdnfs2/* ssdnfs3/* ssdnfs4/* ssdnfs5/*
#smb
#smb
nohup python36 delfile.py /ssdraid/ssdsmb/ssdsmb1 1024 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/smb1.log 300 smb1_file_1K_ >> smb1.nohup 2>&1&
sleep 3
nohup python36 delfile.py /ssdraid/ssdsmb/ssdsmb2 512000 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/smb2.log 600 smb2_file_500K_ >> smb2.nohup 2>&1&
sleep 3
nohup python36 delfile.py /ssdraid/ssdsmb/ssdsmb3 52428800 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/smb3.log 1200 smb3_file_50M_ >> smb3.nohup 2>&1&
sleep 3
nohup python36 deldir.py /ssdraid/ssdsmb/ssdsmb4 11370 8973719772 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/smb4.log 1800 smb4_mu_ >> smb4.nohup 2>&1&
sleep 3
nohup python36 deldir.py /ssdraid/ssdsmb/ssdsmb5 1730 22020096000 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/smb5.log 1800 smb5_M1_ >> smb5.nohup 2>&1&
sleep 3
#ftp
nohup python36 delfile.py /hddraid/hddftp/hddftp1 1024 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/ftp1.log 300 ftp1_file_1K_ >> ftp1.nohup 2>&1&
sleep 3
nohup python36 delfile.py /hddraid/hddftp/hddftp2 512000 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/ftp2.log 600 ftp2_file_500K_ >> ftp2.nohup 2>&1&
sleep 3
nohup python36 delfile.py /hddraid/hddftp/hddftp3 52428800 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/ftp3.log 1200 ftp3_file_50M_ >> ftp3.nohup 2>&1&
sleep 3
nohup python36 deldir.py /hddraid/hddftp/hddftp4 11370 8973719772 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/ftp4.log 1800 ftp4_mu_ >> ftp4.nohup 2>&1&
sleep 3
nohup python36 deldir.py /hddraid/hddftp/hddftp5 1730 22020096000 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/ftp5.log 1800 ftp5_M1_ >> ftp5.nohup 2>&1&
sleep 3
#nfs
nohup python36 delfile.py /ssdraid/ssdnfs/ssdnfs1 1024 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/nfs1.log 300 nfs1_file_1K_ >> nfs1.nohup 2>&1&
sleep 3
nohup python36 delfile.py /ssdraid/ssdnfs/ssdnfs2 512000 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/nfs2.log 600 nfs2_file_500K_ >> nfs2.nohup 2>&1&
sleep 3
nohup python36 delfile.py /ssdraid/ssdnfs/ssdnfs3 52428800 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/nfs3.log 1200 nfs3_file_50M_ >> nfs3.nohup 2>&1&
sleep 3
nohup python36 deldir.py /ssdraid/ssdnfs/ssdnfs4 11370 8973719772 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/nfs4.log 1800 nfs4_mu_ >> nfs4.nohup 2>&1&
sleep 3
nohup python36 deldir.py /ssdraid/ssdnfs/ssdnfs5 1730 22020096000 ".SUTMP:.sutmp:.000001:_sutmp:su_tmp" /hddraid/stability/dest/logs/nfs5.log 1800 nfs5_M1_ >> nfs5.nohup 2>&1&



