# docker run -it --security-opt seccomp=unconfined centos:lastes
# use: ./docker_run.sh 19 10001
# port: from docker-compose.yml
# image name
docker_name="Docker"

docker run -d \
    --rm \
    -h ${docker_name} \
    --name ${docker_name} \
    -v $(pwd):/root/work \
    -p $2:$2 \
    --cap-add=SYS_PTRACE \
    pwn_deploy_pwn_$1


# docker run -it \
#         --rm \
#         --security-opt seccomp=unconfined \
#         -v /root/Tools/DeployPwnChroot/bin:/root/work \
#         -p 10000:10000 \
#         --cap-add=SYS_PTRACE \
#         $1 # pwn_deploy_pwn_19