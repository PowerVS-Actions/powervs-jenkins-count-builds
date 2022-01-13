FROM python:3.10

LABEL maintaner="Rafael Peria de Sene - rpsene@br.ibm.com"
LABEL year="2022"

RUN apt-get update && apt-get upgrade -y && \
apt-get install -y iputils-ping python3-pip libpq-dev \
python-dev build-essential && \
pip3 install python-jenkins urllib3 pytz

WORKDIR /cluster

ENV BUILD_NAME_TO_COUNT=""
ENV POWERVS_JENKINS_URL=""
ENV POWERVS_JENKINS_USER=""
ENV POWERVS_JENKINS_TOKEN=""

ADD ./count_builds.py ./

CMD ["count_builds.py"]

ENTRYPOINT ["/usr/local/bin/python3.10"]
