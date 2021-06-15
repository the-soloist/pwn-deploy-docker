#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-09-17 14:01:13
# @Author  : giantbranch (giantbranch@gmail.com)
# @Link    : http://www.giantbranch.cn/
# @tags : 

# Whether to replace /bin/sh
REPLACE_BINSH = False

FLAG_BAK_FILENAME = "flags.txt"
PORT_INFO_FILENAME = "ports.txt"
PWN_BIN_PATH = "./bin"
XINETD_CONF_FILENAME = "pwn.xinetd"
PORT_LISTEN_START_FROM = 10000

XINETD = '''service ctf
{
    disable = no
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    type        = UNLISTED
    port        = %d
    bind        = 0.0.0.0
    server      = /usr/sbin/chroot   
    server_args = --userspec=%s /home/%s ./%s
    # safety options
    per_source  = 10 # the maximum instances of this service per source IP address
    rlimit_cpu  = 20 # the maximum number of CPU seconds that the service may use
    rlimit_as  = 100M # the Address Space resource limit for the service
    #access_times = 2:00-9:00 12:00-24:00
}

'''

DOCKERFILE = '''FROM ubuntu:16.04
ENV DEBIAN_FRONTEND=noninteractive

# === init
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \\
    apt update && \\
    mkdir /root/.pip && \\
    mkdir /root/Pwn

# === install
RUN apt install -y lib32z1 xinetd && \\
    apt install -y gdb tmux python3 python3-pip

COPY src/pip.conf /root/.pip/pip.conf
COPY src/GdbPlugins/ /root/Pwn/GdbPlugins/

RUN pip3 install pip --upgrade && \\
    pip3 install six --upgrade && \\
    pip3 install pwntools

# === peda pwngdb
# COPY src/gdbinit/.gdbinit-peda /root/.gdbinit

# === pwndbg pwngdb
COPY src/gdbinit/.gdbinit-pwndbg /root/.gdbinit
RUN apt -y install git && \\
    chmod 755 /root/Pwn/GdbPlugins/pwndbg/setup.sh && \\
    cd /root/Pwn/GdbPlugins/pwndbg/ && \\
    ./setup.sh

# === gef pwngdb
# COPY src/gdbinit/.gdbinit-gef /root/.gdbinit
# RUN apt -y install wget
# RUN cd /root/Pwn/GdbPlugins/ && \\
#     wget -q -O- https://github.com/hugsy/gef/raw/master/scripts/gef.sh | sh && \\
#     wget -O ./.gdbinit-gef.py -q https://github.com/hugsy/gef/raw/master/gef.py

# === delete
RUN rm -rf /var/lib/apt/lists/ && \\
    rm -rf /root/.cache && \\
    rm -rf /tmp/* /var/lib/apt/* /var/cache/* /var/log/* && \\
    apt autoclean

# === config
COPY ./pwn-%s'''+XINETD_CONF_FILENAME[3:]+''' /etc/xinetd.d/pwn

COPY ./service.sh /service.sh

RUN chmod +x /service.sh

# useradd and put flag
%s

# copy bin
%s

# chown & chmod
%s

# copy lib,/bin PS: ubuntu>>19.04 need delete 'cp -R /lib* /home/%%s'
%s

CMD ["/service.sh"]
'''

DOCKERCOMPOSE = '''version: '2'
services:
  pwn_deploy_%s:
    image: pwn_deploy_%s:latest
    build:
      context: .
      dockerfile: pwn-%s.Dockerfile
    container_name: pwn_deploy_%s
    ports:
    %s
    volumes:
      - ./bin:/root/work
      
'''