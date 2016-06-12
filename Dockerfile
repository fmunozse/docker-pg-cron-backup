
FROM postgres:9.5.1
MAINTAINER Francisco Munoz <fmunozse@gmail.com>


RUN apt-get update && apt-get install -y \
    python \
    python2.7 \
    python-dev \
    python-setuptools \
    cron \
    ssmtp

VOLUME ["/data/backups"]

ENV BACKUP_DIR /data/backups

ADD ./scripts /backup
RUN chmod +x /backup/*.sh

RUN touch /backup.log


ENTRYPOINT ["/backup/entrypoint.sh"]
CMD cron && tail -f /backup.log


