FROM python:3.8-slim
WORKDIR /opt
COPY updater-version/configs/get_component_version.py ./
COPY updater-version/configs/* ./
RUN chmod 0600 private_ssh_key
RUN apt-get update && apt-get install -y ansible git openssh-client
RUN pip3 install -r requirements.txt
RUN secret=$(cat secret-file.txt|base64 -d) && sed 's/.*/'$secret'/' -i secret-file.txt && ansible-vault decrypt config_dev config_prod --vault-password-file secret-file.txt
ENTRYPOINT ["python3.8", "/opt/get_component_version.py"]