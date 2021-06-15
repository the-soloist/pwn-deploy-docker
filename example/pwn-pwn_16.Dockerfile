FROM ubuntu:16.04
ENV DEBIAN_FRONTEND=noninteractive

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
COPY ./pwn-pwn_16.xinetd /etc/xinetd.d/pwn

COPY ./service.sh /service.sh

RUN chmod +x /service.sh

# useradd and put flag
RUN useradd -m pwn_16 && \
    echo 'flag{951db285-e4c4-410a-b587-111b7328fb67}' > /home/pwn_16/flag
    

# copy bin
COPY ./bin/pwn_16 /home/pwn_16/pwn_16
COPY ./catflag /home/pwn_16/bin/sh


# chown & chmod
RUN chown -R root:pwn_16 /home/pwn_16 && \
    chmod -R 750 /home/pwn_16 && \
    chmod 740 /home/pwn_16/flag
    

# copy lib,/bin PS: ubuntu>>19.04 need delete 'cp -R /lib* /home/%s'
RUN cp -R /lib* /home/pwn_16 && cp -R /usr/lib* /home/pwn_16 && \
    mkdir /home/pwn_16/dev && \
    mknod /home/pwn_16/dev/null c 1 3 && \
    mknod /home/pwn_16/dev/zero c 1 5 && \
    mknod /home/pwn_16/dev/random c 1 8 && \
    mknod /home/pwn_16/dev/urandom c 1 9 && \
    chmod 666 /home/pwn_16/dev/* 

CMD ["/service.sh"]
