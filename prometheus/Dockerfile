FROM prom/prometheus
ADD prometheus.yml /etc/prometheus/
ADD alert.rules /etc/prometheus/
ENTRYPOINT [ "/bin/prometheus" ]
CMD ["-config.file=/etc/prometheus/prometheus.yml", "-alertmanager.url=http://prometheus-alertmanager.internal.aptitudelabs.com/"]
