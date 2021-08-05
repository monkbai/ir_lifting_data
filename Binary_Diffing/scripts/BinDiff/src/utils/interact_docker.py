import os

from src.utils.config import *
from src.utils.log import log

CP = 'sudo docker cp'
DOCKER_RUN = 'sudo docker exec -i'


def cp_file_from_docker(src: str, to: str):
    cp_cmd = "{} {}:{} {}".format(CP, CONTAINER_ID, src, to)
    log(cp_cmd, 'RUN CMD')
    os.system(cp_cmd)
    log('Finish')


def run_cmd_in_docker(cmd):
    run_cmd = '{} {} bash -c \"{}\"'.format(DOCKER_RUN, CONTAINER_ID, cmd)
    log(cmd, 'DOCKER RUN CMD')
    os.system(run_cmd)
    log('Finish')
