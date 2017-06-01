FROM node:7-alpine

MAINTAINER Bipin Thite<bipin.thite@aptitudelabs.com>

RUN apk update \
  && apk add --update alpine-sdk \
  && npm install -g @angular/cli@1.0.0-rc.1 \
  && ng set --global packageManager=yarn \
  && apk del alpine-sdk \
  && rm -rf /tmp/* /var/cache/apk/* *.tar.gz ~/.npm \
  && npm cache clear \
  && sed -i -e "s/bin\/ash/bin\/sh/" /etc/passwd

CMD ["ng"]
