#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-17 14:32:32
# @Author  : giantbranch (giantbranch@gmail.com)
# @Link    : http://www.giantbranch.cn/
# @tags : 

from config import *
import os
import uuid
import json

def getFileList():
    filelist = []
    for filename in os.listdir(PWN_BIN_PATH):
        filelist.append(filename)
    filelist.sort()
    return filelist

def isExistBeforeGetFlagAndPort(filename, contentBefore):
    filename_tmp = ""
    tmp_dict = ""
    ret = False
    for line in contentBefore:
        tmp_dict = json.loads(line)
        filename_tmp = tmp_dict["filename"]
        if filename == filename_tmp:
            ret = [tmp_dict["flag"], tmp_dict["port"]]
    return ret

def generateFlags(filelist):
    tmp_flag = ""
    contentBefore = []
    if not os.path.exists(FLAG_BAK_FILENAME):
        os.popen("touch " + FLAG_BAK_FILENAME)

    with open(FLAG_BAK_FILENAME, 'r') as f:
        while 1:
            line = f.readline()
            if not line:
                break
            contentBefore.append(line)
    # bin's num != flags.txt's linenum, empty the flags.txt
    if len(filelist) != len(contentBefore):
        os.popen("echo '' > " + FLAG_BAK_FILENAME)
        contentBefore = []
    port = PORT_LISTEN_START_FROM + len(contentBefore)
    flags = []
    with open(FLAG_BAK_FILENAME, 'w') as f:
        for filename in filelist:
            flag_dict = {}
            ret = isExistBeforeGetFlagAndPort(filename, contentBefore)
            if ret == False:
                tmp_flag = "flag{" + str(uuid.uuid4()) + "}"
                flag_dict["port"] = port
                port = port + 1
            else:
                tmp_flag = ret[0]
                flag_dict["port"] = ret[1]

            flag_dict["filename"] = filename
            flag_dict["flag"] = tmp_flag
            flag_json = json.dumps(flag_dict)
            print flag_json
            f.write(flag_json + "\n")
            flags.append(tmp_flag)
    return flags

def generateXinetd(filename):
    contentBefore = []
    with open(FLAG_BAK_FILENAME, 'r') as f:
        while 1:
            line = f.readline()
            if not line:
                break
            contentBefore.append(line)
    
    uid = 1000
    # for filename in filelist:
    conf = ""
    port = isExistBeforeGetFlagAndPort(filename, contentBefore)[1]
    conf += XINETD % (port, str(uid) + ":" + str(uid), filename, filename)
    # uid = uid + 1
    with open("pwn-{}{}".format(filename,XINETD_CONF_FILENAME[3:]), 'w') as f:
        f.write(conf)

def generateDockerfile(filename, flag):
    conf = ""

    # useradd and put flag
    runcmd="""RUN useradd -m %s && \\
    echo '%s' > /home/%s/flag
    """
    runcmd = runcmd % (filename,flag,filename)
    # print runcmd 

    # copy bin
    copybin = ""
    copybin += "COPY " + PWN_BIN_PATH + "/" + filename  + " /home/" + filename + "/" + filename + "\n"
    copybin += "COPY ./catflag" + " /home/" + filename + "/bin/sh\n"

    # print copybin

    # chown & chmod
    chown_chmod="""RUN chown -R root:%s /home/%s && \\
    chmod -R 750 /home/%s && \\
    chmod 740 /home/%s/flag
    """
    chown_chmod = chown_chmod%(filename,filename,filename,filename)
    # print chown_chmod

    # copy lib,/bin 
    # dev = '''mkdir /home/%s/dev && mknod /home/%s/dev/null c 1 3 && mknod /home/%s/dev/zero c 1 5 && mknod /home/%s/dev/random c 1 8 && mknod /home/%s/dev/urandom c 1 9 && chmod 666 /home/%s/dev/* && '''
    dev = '''
    mkdir /home/%s/dev && \\
    mknod /home/%s/dev/null c 1 3 && \\
    mknod /home/%s/dev/zero c 1 5 && \\
    mknod /home/%s/dev/random c 1 8 && \\
    mknod /home/%s/dev/urandom c 1 9 && \\
    chmod 666 /home/%s/dev/* '''
    if REPLACE_BINSH:
        # ness_bin = '''mkdir /home/%s/bin && cp /bin/sh /home/%s/bin && cp /bin/ls /home/%s/bin && cp /bin/cat /home/%s/bin'''
        ness_bin = '''&& \\
    cp /bin/sh /home/%s/bin && \\
    cp /bin/ls /home/%s/bin && \\
    cp /bin/cat /home/%s/bin'''
        # print ness_bin

    copy_lib_bin_dev="""RUN cp -R /lib* /home/%s && cp -R /usr/lib* /home/%s && \\"""
    copy_lib_bin_dev=copy_lib_bin_dev % (filename,filename)
    copy_lib_bin_dev += dev % (filename, filename, filename, filename, filename, filename)

    if REPLACE_BINSH:
        copy_lib_bin_dev += ness_bin % (filename, filename, filename)
    pass                


    # print copy_lib_bin_dev

    conf = DOCKERFILE % (filename,runcmd, copybin, chown_chmod, copy_lib_bin_dev)
    
    with open('pwn-{}.Dockerfile'.format(filename), 'w') as f:
        f.write(conf)

def generateDockerCompose(filelist,length):
    conf = '''version: '2'
services:
'''
    for filename,index in zip(filelist,range(length)):
        # print filename,index
        ports = ""
        port = PORT_LISTEN_START_FROM +index
        ports += "- " + str(port) + ":" + str(port) + "\n"

        conf += DOCKERCOMPOSE[23:] % (filename,filename,filename,filename,ports)
        # print conf
    with open("docker-compose.yml", 'w') as f:
        f.write(conf)

# def generateBinPort(filelist):
#     port = PORT_LISTEN_START_FROM
#     tmp = ""
#     for filename in filelist:
#         tmp += filename  + "'s port: " + str(port) + "\n"
#         port = port + 1
#     print tmp
#     with open(PORT_INFO_FILENAME, 'w') as f:
#         f.write(tmp)
    
filelist = getFileList()
flags = generateFlags(filelist)

# print flags
# generateBinPort(filelist)

for filename in filelist:
    generateXinetd(filename)

for filename,flag in zip(filelist,flags):
    # print flag
    generateDockerfile(filename, flag)


# generateDockerfile(filelist[0], flags)
generateDockerCompose(filelist,len(filelist))



