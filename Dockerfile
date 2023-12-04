FROM dockyard.armada.sh/microservice_go_focal
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV MICROSERVICE_NAME dockyard-v2
ENV DOCKYARD_V2_UPDATE_DATE 2023-11-29

ADD scripts/install_docker_registry.sh /tmp/
RUN cd /tmp && chmod +x install_docker_registry.sh && sync && ./install_docker_registry.sh

RUN pip install -U armada nested_dict pyyaml

ADD . /opt/dockyard-v2
ADD ./supervisor/* /etc/supervisor/conf.d/
RUN ln -s /opt/dockyard-v2/scripts/remove_image.py /usr/local/bin/remove_image

RUN cp /opt/dockyard-v2/scripts/clean_orphaned_images.sh /usr/local/bin/clean_orphaned_images
RUN chmod +x /usr/local/bin/clean_orphaned_images

RUN ( crontab -l; echo "21 2 * * 0 /usr/local/bin/clean_orphaned_images" ) | crontab -

EXPOSE 80
