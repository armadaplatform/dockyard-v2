FROM microservice_go
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV DOCKYARD_V2_UPDATE_DATE 2016-10-05

ADD scripts/install_docker_registry.sh /tmp/
RUN cd /tmp && chmod +x install_docker_registry.sh && sync && ./install_docker_registry.sh

RUN pip install -U armada nested_dict pyyaml

ADD . /opt/dockyard-v2
ADD ./supervisor/* /etc/supervisor/conf.d/
RUN ln -s /opt/dockyard-v2/scripts/remove_image.py /usr/local/bin/remove_image

EXPOSE 80
