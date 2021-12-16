www.mlb.com から大谷 翔平選手のホームラン数を取得します。

## 実行に必要なもの

- [Docker](https://www.docker.com)
- Python 3.9.2
- Amazon Web Services
  - Amazon ECR
  - AWS CodeCommit
  - AWS Batch
  - AWS CloudWatch

## 開発環境

EC2(Amazon Linux 2)環境を前提とします。

### 1. 初期セットアップ

```
sudo yum -y update
sudo yum -y install git python-pip
sudo pip install pipenv
git clone https://github.com/yyuu/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
source ~/.bash_profile
sudo yum -y install gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel
pyenv install 3.9.2
git clone https://github.com/ikayarou/notice_shoheiOhtani_homeruns.git
cd notice_shoheiOhtani_homeruns
```

### 2. Google Chrome、日本語フォントのインストール

```
sudo curl https://intoli.com/install-google-chrome.sh | bash
sudo yum install -y "google-noto*"
```

### 3. Python 実行環境の作成

```
cd notice_shoheiOhtani_homeruns
pyenv local 3.9.2
pipenv --python 3.9.2
pipenv shell
pipenv sync --dev
```

### 4. ローカルでの実行

```
PATH=$PATH:`chromedriver-path` python handler.py
```

Returns

```
2018: 22
2019: 18
2020: 7
2021: 46
```

## 本番環境

### 1. CodeCommit への ソースコードの Push

`notice_shoheiOhtani_homeruns` リポジトリ(名称固定)を作成し `master` ブランチに最新のコードを Push します。

```
git remote add prod ssh://APKxxxxxxxxxxxxxxxxx@git-codecommit.ap-northeast-1.amazonaws.com/v1/repos/notice_shoheiOhtani_homeruns
git push prod master
```

### 2. ECR への Docker Image の Push

```
docker build -t notice-ohtani-homeruns .
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin xxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com
docker tag notice-ohtani-homeruns:latest xxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
docker push xxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
```

### 3. AWS Batch の作成

`手順3` で ECR に Push した Docke Image を利用する設定内容にて、AWS Batch を作成します。

`Job definition` の設定については、以下にご注意ください。

| 項目 | 説明 | サンプル値 |
| --- | --- | --- |
| Image | 手順3でPushしたイメージ | xxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest |
| Command syntax | /bin/bash /opt/ikayarou/run.sh | 固定値 |
| Job role | CodeCommit から clone できる権限 | 面倒だったので PowerUser 権限を付与しちゃいました |
| Execution role | CodeCommit から clone できる権限 | 面倒だったので PowerUser 権限を付与しちゃいました |
| Environment variables | タイムゾーン | TZ: Asia/Tokyo |

### 4. スケジューラの設定

CloudWatch Events Rule から `手順3` で作成した AWS Batch を起動するように設定します。  
`0 1 ? * FRI *` では、毎週金曜日の `10:00` に起動するように設定しています。（GMT）
