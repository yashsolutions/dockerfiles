FROM ubuntu:16.04
RUN apt-get update && apt-get install -y python-dev haproxy python-pip supervisor
RUN pip install flask requests
ADD update_config.py /update_config.py
RUN chmod +x /update_config.py
ADD supervisor.conf /etc/supervisor/conf.d/supervisor.conf
EXPOSE 80
CMD ["/usr/bin/supervisord"]

