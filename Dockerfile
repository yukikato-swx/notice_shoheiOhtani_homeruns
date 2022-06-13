FROM amazonlinux:latest

SHELL ["/bin/bash", "-c"]

RUN yum update -y \
  && curl https://intoli.com/install-google-chrome.sh | bash \
  && yum install -y google-noto* gcc gcc-c++ make git openssl-devel bzip2-devel zlib-devel readline-devel libffi-devel patch tar awscli \
  && yum clean all \
  && git clone https://github.com/pyenv/pyenv.git /usr/local/pyenv \
  && echo 'export PYENV_ROOT="/usr/local/pyenv"' | tee -a /etc/profile.d/pyenv.sh \
  && echo 'export PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"' | tee -a /etc/profile.d/pyenv.sh \
  && echo 'eval "$(pyenv init -)"' | tee -a /etc/profile.d/pyenv.sh \
  && source /etc/profile.d/pyenv.sh && pyenv install 3.9.2 && pyenv global 3.9.2 && pip install --upgrade pip && pip install pipenv \
  && mkdir -p /opt/yukikato-swx \
  && chmod 777 /opt/yukikato-swx

COPY run.sh /opt/yukikato-swx/run.sh
