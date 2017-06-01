FROM ruby:2.2
MAINTAINER kiyoto@treausuredata.com
RUN apt-get update
RUN gem install fluentd -v "0.14.14"
RUN mkdir /etc/fluent
RUN apt-get install -y libcurl4-gnutls-dev make
RUN /usr/local/bin/gem install fluent-plugin-elasticsearch
RUN /usr/local/bin/gem install fluent-plugin-redis
RUN /usr/local/bin/gem install fluent-plugin-redis-store
ADD fluent.conf /etc/fluent/
ENTRYPOINT ["/usr/local/bundle/bin/fluentd", "-c", "/etc/fluent/fluent.conf"]
