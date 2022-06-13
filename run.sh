#!/bin/bash

source /etc/profile.d/pyenv.sh
mkdir -p /opt/yukikato-swx/notice_shoheiOhtani_homeruns
git clone --config credential.helper='!aws --region ap-northeast-1 codecommit credential-helper $@' --config credential.UseHttpPath=true https://git-codecommit.ap-northeast-1.amazonaws.com/v1/repos/notice_shoheiOhtani_homeruns /opt/yukikato-swx/notice_shoheiOhtani_homeruns
cd /opt/yukikato-swx/notice_shoheiOhtani_homeruns
pipenv install
PATH=$PATH:`pipenv run chromedriver-path` pipenv run python handler.py

exit 0
