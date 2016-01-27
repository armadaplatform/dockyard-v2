FROM microservice_python3
MAINTAINER Cerebro <cerebro@ganymede.eu>

ENV DOCKYARD_V2_APT_GET_UPDATE_DATE 2016-01-27
#
#RUN apt-get update
#RUN apt-get install -y g++ gcc libc6-dev make wget librados-dev apache2-utils git
#
#ENV GOLANG_VERSION 1.5.3
#ENV GOLANG_DOWNLOAD_URL https://golang.org/dl/go$GOLANG_VERSION.linux-amd64.tar.gz
#ENV GOLANG_DOWNLOAD_SHA256 43afe0c5017e502630b1aea4d44b8a7f059bf60d7f29dfd58db454d4e4e0ae53
#
#RUN curl -fsSL "$GOLANG_DOWNLOAD_URL" -o golang.tar.gz \
#	&& echo "$GOLANG_DOWNLOAD_SHA256  golang.tar.gz" | sha256sum -c - \
#	&& tar -C /usr/local -xzf golang.tar.gz \
#	&& rm golang.tar.gz
#
#ENV GOPATH /go
#ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH
#
#RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

ADD scripts /tmp/scripts
RUN cd /tmp/scripts && chmod +x install_go.sh && sync && ./install_go.sh

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

RUN mkdir -p "$GOPATH/src" "$GOPATH/bin"
RUN chmod -R 777 "$GOPATH"

#RUN wget https://raw.githubusercontent.com/docker-library/golang/master/1.5/go-wrapper -O /usr/local/bin/go-wrapper
#RUN chmod +x /usr/local/bin/go-wrapper

RUN apt-get update
RUN apt-get install -y librados-dev apache2-utils git

ENV CHECKOUT_DIR /go/src/github.com/docker
ENV DISTRIBUTION_DIR $CHECKOUT_DIR/distribution
ENV GOPATH $DISTRIBUTION_DIR/Godeps/_workspace:$GOPATH
ENV DOCKER_BUILDTAGS include_rados include_oss include_gcs

RUN mkdir -p $CHECKOUT_DIR
WORKDIR $CHECKOUT_DIR
RUN git clone -b v2.2.1 --single-branch --depth 1 https://github.com/docker/distribution.git

WORKDIR $DISTRIBUTION_DIR

RUN mkdir -p /etc/docker/registry/
RUN cp cmd/registry/config-dev.yml /etc/docker/registry/config.yml

RUN make PREFIX=/go clean binaries

RUN mkdir -p /var/lib/registry
RUN chmod 777 /var/lib/registry

ADD . /opt/dockyard-v2
ADD ./supervisor/* /etc/supervisor/conf.d/

RUN rm -f /etc/supervisor/conf.d/update_haproxy.conf
RUN sed 's/80/5000/' /etc/supervisor/conf.d/register_in_service_discovery.conf -i

EXPOSE 5000
