FROM ubuntu:16.04
RUN apt-get update && apt-get install -y python-dev nginx python-pip supervisor
RUN pip install flask requests
ADD update_config.py /update_config.py
ADD nginx.conf /etc/nginx/nginx.conf
ADD 503.html /503.html
RUN chmod +x /update_config.py
ADD supervisor.conf /etc/supervisor/conf.d/supervisor.conf
EXPOSE 80
CMD ["/usr/bin/supervisord"]

