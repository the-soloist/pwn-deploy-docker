FROM ubuntu:19.04

# === init
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    apt update && \
    mkdir /root/.pip && \
    mkdir /root/Pwn

# === install
RUN apt install -y lib32z1 xinetd && \
    apt install -y gdb tmux python3 python3-pip

COPY src/pip.conf /root/.pip/pip.conf
COPY src/GdbPlugins/ /root/Pwn/GdbPlugins/

RUN pip3 install pip --upgrade && \
    pip3 install six --upgrade && \
    pip3 install pwntools

# === peda pwngdb
# COPY src/gdbinit/.gdbinit-peda /root/.gdbinit

# === pwndbg pwngdb
COPY src/gdbinit/.gdbinit-pwndbg /root/.gdbinit
RUN apt -y install git && \
    chmod 755 /root/Pwn/GdbPlugins/pwndbg/setup.sh && \
    cd /root/Pwn/GdbPlugins/pwndbg/ && \
    ./setup.sh

# === gef pwngdb
# COPY src/gdbinit/.gdbinit-gef /root/.gdbinit
# RUN apt -y install wget
# RUN cd /root/Pwn/GdbPlugins/ && \
#     wget -q -O- https://github.com/hugsy/gef/raw/master/scripts/gef.sh | sh && \
#     wget -O ./.gdbinit-gef.py -q https://github.com/hugsy/gef/raw/master/gef.py

# === delete
RUN rm -rf /var/lib/apt/lists/ && \
    rm -rf /root/.cache && \
    rm -rf /tmp/* /var/lib/apt/* /var/cache/* /var/log/* && \
    apt autoclean

# === config
COPY ./pwn-pwn_19.xinetd /etc/xinetd.d/pwn

COPY ./service.sh /service.sh

RUN chmod +x /service.sh

# useradd and put flag
RUN useradd -m pwn_19 && \
    echo 'flag{d13c6ee2-9662-4099-bc4b-50d8bdd74c11}' > /home/pwn_19/flag
    

# copy bin
COPY ./bin/pwn_19 /home/pwn_19/pwn_19
COPY ./catflag /home/pwn_19/bin/sh


# chown & chmod
RUN chown -R root:pwn_19 /home/pwn_19 && \
    chmod -R 750 /home/pwn_19 && \
    chmod 740 /home/pwn_19/flag
    

# copy lib,/bin >> ubuntu:19.04 need delete 'cp -R /lib* /home/%s'
RUN cp -R /usr/lib* /home/pwn_19 && \
    mkdir /home/pwn_19/dev && \
    mknod /home/pwn_19/dev/null c 1 3 && \
    mknod /home/pwn_19/dev/zero c 1 5 && \
    mknod /home/pwn_19/dev/random c 1 8 && \
    mknod /home/pwn_19/dev/urandom c 1 9 && \
    chmod 666 /home/pwn_19/dev/* 

CMD ["/service.sh"]
