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

### 1. Google Chrome、日本語フォントのインストール

```
$ sudo curl https://intoli.com/install-google-chrome.sh | bash
$ sudo yum install -y "google-noto*"
```

### 2. Python 実行環境の作成

```
$ pyenv local 3.9.2
$ pipenv --python 3.9.2
$ pipenv shell
$ pipenv sync --dev
```

### 3. ローカルでの実行

```
$ PATH=$PATH:`chromedriver-path` python handler.py
```

## 本番環境

### 1. CodeCommit への ソースコードの Push

`notice_shoheiOhtani_homeruns` リポジトリ(名称固定)を作成し `master` ブランチに最新のコードを Push します。

```
$ git remote add prod ssh://APKxxxxxxxxxxxxxxxxx@git-codecommit.ap-northeast-1.amazonaws.com/v1/repos/notice_shoheiOhtani_homeruns
$ git push prod master
```

### 2. ECR への Docker Image の Push

```
$ docker build -t notice-ohtani-homeruns .
$ aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin xxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com
$ docker tag notice-ohtani-homeruns:latest xxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
$ docker push xxxxxxxxxxxx.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
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
