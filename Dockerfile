FROM amazonlinux

SHELL ["/bin/bash", "-c"]

RUN yum update -y

RUN curl https://intoli.com/install-google-chrome.sh | bash

RUN yum install -y google-noto* gcc gcc-c++ make git openssl-devel bzip2-devel zlib-devel readline-devel libffi-devel patch tar awscli

RUN git clone https://github.com/pyenv/pyenv.git /usr/local/pyenv
RUN echo 'export PYENV_ROOT="/usr/local/pyenv"' | tee -a /etc/profile.d/pyenv.sh
RUN echo 'export PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"' | tee -a /etc/profile.d/pyenv.sh
RUN echo 'eval "$(pyenv init -)"' | tee -a /etc/profile.d/pyenv.sh
RUN source /etc/profile.d/pyenv.sh && pyenv install 3.9.2 && pyenv global 3.9.2 && pip install --upgrade pip && pip install pipenv

RUN mkdir -p /opt/ikayarou
RUN chmod 777 /opt/ikayarou
ADD run.sh /opt/ikayarou/run.sh
