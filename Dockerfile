FROM microservice_python3
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV DOCKYARD_V2_APT_GET_UPDATE_DATE 2016-01-27

ADD scripts/install_go.sh /tmp/
RUN cd /tmp && chmod +x install_go.sh && sync && ./install_go.sh

ADD scripts/install_docker_registry.sh /tmp/
RUN cd /tmp && chmod +x install_docker_registry.sh && sync && ./install_docker_registry.sh

ADD . /opt/dockyard-v2
ADD ./supervisor/* /etc/supervisor/conf.d/

RUN rm -f /etc/supervisor/conf.d/update_haproxy.conf
RUN sed 's/80/5000/' /etc/supervisor/conf.d/register_in_service_discovery.conf -i

EXPOSE 5000
