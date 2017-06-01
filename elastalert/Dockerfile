FROM iron/python:2
ENV SET_CONTAINER_TIMEZONE false
ENV CONTAINER_TIMEZONE Asia/Kolkata
ENV ELASTALERT_URL https://github.com/Yelp/elastalert/archive/master.zip
ENV CONFIG_DIR /opt/config
ENV RULES_DIRECTORY /opt/rules
ENV ELASTALERT_CONFIG ${CONFIG_DIR}/elastalert_config.yaml
ENV LOG_DIR /opt/logs
ENV ELASTALERT_DIRECTORY_NAME elastalert
ENV ELASTALERT_HOME /opt/${ELASTALERT_DIRECTORY_NAME}
ENV ELASTALERT_SUPERVISOR_CONF ${CONFIG_DIR}/elastalert_supervisord.conf
ENV ELASTICSEARCH_HOST 10.0.5.4
ENV ELASTICSEARCH_PORT 9200

WORKDIR /opt

COPY ./start-elastalert.sh /opt/

RUN apk update && apk upgrade
RUN apk add ca-certificates openssl-dev libffi-dev python-dev gcc musl-dev tzdata openntpd && \
    rm -rf /var/cache/apk/* && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
    wget ${ELASTALERT_URL} && \
    unzip *.zip && \
    rm *.zip && \
    mv e* ${ELASTALERT_DIRECTORY_NAME}

WORKDIR ${ELASTALERT_HOME}

RUN python setup.py install && \
    pip install -e . && \
    pip uninstall twilio --yes && \
    pip install twilio==6.0.0 && \
    easy_install supervisor && \
    chmod +x /opt/start-elastalert.sh && \
    mkdir -p ${RULES_DIRECTORY} && \
    mkdir -p ${LOG_DIR} && \
    mkdir -p /var/empty

ADD config.yaml ${ELASTALERT_HOME}/config.yaml
ADD smtp_auth_file.yaml ${CONFIG_DIR}/smtp_auth_file.yaml
COPY frequency.yaml ${RULES_DIRECTORY}/frequency.yaml
COPY config-ms_error.yaml ${RULES_DIRECTORY}/match_error.yaml

CMD ["/opt/start-elastalert.sh"]
