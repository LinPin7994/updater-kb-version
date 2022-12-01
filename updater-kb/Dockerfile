FROM python:3.8-slim
WORKDIR /opt
COPY updater-kb/src/* ./
RUN apt-get update && apt-get install git openssh-client -y
RUN chmod 0600 private_ssh_key
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3.8", "/opt/kb_updater.py"]