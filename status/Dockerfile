FROM ubuntu
RUN apt-get update && apt-get install -y python-pip supervisor iputils-ping
RUN pip install tornado redis requests
ADD server.py /server.py
ADD status_check.py /status_check.py
RUN chmod +x /server.py /status_check.py
ADD server.conf /etc/supervisor/conf.d/server.conf
ADD status_check.conf /etc/supervisor/conf.d/status_check.conf
EXPOSE 9000
CMD ["/usr/bin/supervisord"]
