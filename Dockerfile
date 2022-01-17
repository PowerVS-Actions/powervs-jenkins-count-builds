FROM python:3.9

LABEL maintaner="Rafael Peria de Sene - rpsene@br.ibm.com"
LABEL year="2022"

RUN apt-get update && apt-get upgrade -y && \
apt-get install -y python3-pip libpq-dev iputils-ping \
python-dev build-essential && \
pip3 install urllib3 pytz multi_key_dict requests six

RUN git clone https://opendev.org/jjb/python-jenkins.git && cd ./python-jenkins && python3 setup.py install

WORKDIR /cluster

ENV BUILD_NAME_TO_COUNT=""
ENV POWERVS_JENKINS_URL=""
ENV POWERVS_JENKINS_USER=""
ENV POWERVS_JENKINS_TOKEN=""

ADD ./count_builds.py ./

CMD ["count_builds.py"]

ENTRYPOINT ["/usr/local/bin/python3.9"]
