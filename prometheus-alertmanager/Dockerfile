FROM prom/alertmanager
ADD alertmanager.yml /etc/alertmanager/
ADD alertmanager.conf /etc/alertmanager/
ENTRYPOINT [ "/bin/alertmanager" ]
CMD ["-config.file=/etc/alertmanager/alertmanager.yml"]
