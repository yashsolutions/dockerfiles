FROM ubuntu
RUN apt-get update && apt-get install -y python-pip supervisor iputils-ping
RUN pip install tornado redis requests python-jenkins
ADD server.py /server.py
RUN chmod +x /server.py
ADD server.conf /etc/supervisor/conf.d/server.conf
EXPOSE 9000
CMD ["/usr/bin/supervisord"]
