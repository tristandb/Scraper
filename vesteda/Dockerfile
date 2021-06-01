FROM python:3.8-slim-buster

RUN apt-get update && apt-get -y install cron vim

WORKDIR /app

# Copy cron file to the cron.d directory
COPY vesteda-crontab /etc/cron.d/vesteda-crontab

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/vesteda-crontab

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN /usr/bin/crontab /etc/cron.d/vesteda-crontab

RUN echo $PYTHONPATH

# run crond as main process of container
CMD ["bash", "run.sh"]  