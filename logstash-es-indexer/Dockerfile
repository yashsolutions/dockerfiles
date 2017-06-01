FROM docker.elastic.co/logstash/logstash:5.2.2
RUN rm -f /usr/share/logstash/pipeline/logstash.conf
ADD es-indexer.conf /usr/share/logstash/pipeline/es-indexer.conf
RUN echo "xpack.monitoring.enabled: false" >> /usr/share/logstash/config/logstash.yml

