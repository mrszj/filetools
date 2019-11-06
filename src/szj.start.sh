#!/bin/bash
#删除源文件
#cd /hddraid/hddftp/
#rm -fr hddftp1/* hddftp2/* hddftp3/* hddftp4/* hddftp5/*
#cd /ssdraid/ssdsmb/
#rm -fr ssdsmb1/* ssdsmb/* ssdsmb3/* ssdsmb4/* ssdsmb5/*
#cd /hddraid/stability/source
#rm -f logs/*
#cd /ssdraid/ssdnfs/
#rm -rf ssdnfs1/* ssdnfs2/* ssdnfs3/* ssdnfs4/* ssdnfs5/*

sleep 3
#smb
#smb
nohup python36 copyfile.py /ssdraid/stability/source/1K.txt /ssdraid/ssdsmb/ssdsmb1/ /hddraid/stability/source/logs/smb1.log 30 20 smb1_file_1K_ >> smb1.nohup 2>&1&
sleep 3
nohup python36 copyfile.py /ssdraid/stability/source/500K.txt /ssdraid/ssdsmb/ssdsmb2/ /hddraid/stability/source/logs/smb2.log 30 20 smb2_file_500K_ >> smb2.nohup 2>&1&
sleep 3
nohup python36 copyfile.py /ssdraid/stability/source/50M.txt /ssdraid/ssdsmb/ssdsmb3/ /hddraid/stability/source/logs/smb3.log 30 5 smb3_file_50M_ >> smb3.nohup 2>&1&
sleep 3
nohup runuser -l ssdsmb4 -c "python36 /hddraid/stability/source/copydir.py /ssdraid/stability/source/mu /ssdraid/ssdsmb/ssdsmb4/ /hddraid/stability/source/logs/smb4.log 3600  2 smb4_mu_" >> smb4.nohup 2>&1&
sleep 3
nohup runuser -l ssdsmb5 -c "python36 /hddraid/stability/source/copydir.py /ssdraid/stability/source/M1 /ssdraid/ssdsmb/ssdsmb5/ /hddraid/stability/source/logs/smb5.log 3600  2 smb5_M1_" >> smb5.nohup 2>&1&
sleep 3

#ftp
nohup python36 copyfile.py /ssdraid/stability/source/1K.txt /hddraid/hddftp/hddftp1/ /hddraid/stability/source/logs/ftp1.log 30 20 ftp1_file_1K_ >> ftp1.nohup 2>&1&
sleep 3
nohup python36 copyfile.py /ssdraid/stability/source/500K.txt /hddraid/hddftp/hddftp2/ /hddraid/stability/source/logs/ftp2.log 30 20 ftp2_file_500K_ >> ftp2.nohup 2>&1&
sleep 3
nohup python36 copyfile.py /ssdraid/stability/source/50M.txt /hddraid/hddftp/hddftp3/ /hddraid/stability/source/logs/ftp3.log 30 5 ftp3_file_50M_ >> ftp3.nohup 2>&1&
sleep 3
nohup runuser -l hddftp4 -c "python36 /hddraid/stability/source/copydir.py /ssdraid/stability/source/mu /hddraid/hddftp/hddftp4/ /hddraid/stability/source/logs/ftp4.log 1800  2 ftp4_mu_" >> ftp4.nohup 2>&1&
sleep 3
nohup runuser -l hddftp5 -c "python36 /hddraid/stability/source/copydir.py /ssdraid/stability/source/M1 /hddraid/hddftp/hddftp5/ /hddraid/stability/source/logs/ftp5.log 1800  2 ftp5_M1_" >> ftp5.nohup 2>&1&
sleep 3

#nfs
nohup python36 copyfile.py /ssdraid/stability/source/1K.txt /ssdraid/ssdnfs/ssdnfs1/ /hddraid/stability/source/logs/nfs1.log 60 20 nfs1_file_1K_ >> nfs1.nohup 2>&1&
sleep 3
nohup python36 copyfile.py /ssdraid/stability/source/500K.txt /ssdraid/ssdnfs/ssdnfs2/ /hddraid/stability/source/logs/nfs2.log 60 60 nfs2_file_500K_ >> nfs2.nohup 2>&1&
sleep 3
nohup python36 copyfile.py /ssdraid/stability/source/50M.txt /ssdraid/ssdnfs/ssdnfs3/ /hddraid/stability/source/logs/nfs3.log 60 5 nfs3_file_50M_ >> nfs3.nohup 2>&1&
sleep 3
nohup python36 /hddraid/stability/source/copydir.py /ssdraid/stability/source/mu /ssdraid/ssdnfs/ssdnfs4/ /hddraid/stability/source/logs/nfs4.log 3600  1 nfs4_mu_ >> nfs4.nohup 2>&1&
sleep 3
nohup python36 /hddraid/stability/source/copydir.py /ssdraid/stability/source/M1 /ssdraid/ssdnfs/ssdnfs5/ /hddraid/stability/source/logs/nfs5.log 3600  1 nfs5_M1_ >> nfs5.nohup 2>&1&


