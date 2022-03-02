www.mlb.com から大谷 翔平選手のホームラン数を取得し、Slackへ投稿します。

![top-page](https://raw.githubusercontent.com/ikayarou/notice_shoheiOhtani_homeruns/images/shohei.jpg)

## 実行に必要なもの

- [Docker](https://www.docker.com)
- Python 3.9.2
- Amazon Web Services
  - Amazon DynamoDB
  - Amazon ECR
  - Amazon EventBridge
  - AWS Batch
  - AWS CodeCommit
  - AWS Key Management Service
  - AWS Systems Manager パラメータストア
- CI/CD
  - AWS CodeDeploy
  - AWS CodePipeline
  - GitHub Actions

## 開発環境

### 1. Slack Appの作成

1. [Your Apps](https://api.slack.com/apps?new_app=1) からSlackのアプリケーションを作成します
2. 左のカラムの OAuth & Permissions に移動します
3. Scope から Add an OAuth Scope を押して、 chat:write を追加します
4. OAuth Tokens for Your Workspace から Token を取得します
5. Slackの任意のチャンネル上で作成したSlack Appを参加させます

### 2. パラメータストア用のCMK作成

パラメータストアのSecureStringに使用するCMKを作成します。

| 名前 | その他 |
| --- | --- |
| /param/shohei_ohtani_bot | すべてデフォルト |

### 3. パラメータストアのセットアップ

機密情報の登録や可変となる値はパラメータストア上で管理します。

| 名前 | タイプ | データ型 | 値 | 説明 |
| --- | --- | --- | --- | --- |
| /shohei_ohtani_bot/aws_account | String | text | 123456789012 | AWSアカウントを入力します。 |
| /shohei_ohtani_bot/current_season_year | String | text | 2021 | ホームラン数を取得する年を入力します。 |
| /shohei_ohtani_bot/current_season_row | String | text | row-3 | ホームラン数が記録されている行を入力します。 <br> 2020年は「row-2」、2021年は「row-3」。 |
| /shohei_ohtani_bot/slack_bot_token | SecureString | text | XXXXXXXX | SlackBotのトークンを入力します。 <br> CMKは前手順で作成したものを指定します。 |
| /shohei_ohtani_bot/slack_channel | String | text | #slack-channel | Slackの投稿先チャンネルを入力します。 |

### 4. リポジトリをFork

本リポジトリをForkします。

### 5. EC2セットアップ

EC2(Amazon Linux 2)にPowerUser権限のIAMロールを付与していることを前提とします。

<> 初期セットアップ

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
git clone https://github.com/xxxxxxx/notice_shoheiOhtani_homeruns.git
cd notice_shoheiOhtani_homeruns
```

<> Google Chrome、日本語フォントのインストール

```
sudo curl https://intoli.com/install-google-chrome.sh | bash
sudo yum install -y "google-noto*"
```

<> Python 実行環境の作成

```
cd notice_shoheiOhtani_homeruns
pyenv local 3.9.2
pipenv --python 3.9.2
pipenv shell
pipenv sync --dev
```

### 6. ローカルでの実行

```
PATH=$PATH:`chromedriver-path` python handler.py
```

※Chromeのバージョンエラー発生時は以下のコマンドでバージョンを揃えてください。

<> Google Chromeのインストール

```
sudo curl https://intoli.com/install-google-chrome.sh | bash
```

<> Google Chromeのバージョン`98.0.4758.102`がインストールされた場合に`chromedriver-binary`のバージョンを指定してインストール

```
pipenv install chromedriver-binary~=98.0.4758.102
```

## 本番環境

### 1. 文字列の置換

文字列`ikayarou`を自身のGitHubユーザー名に置換します。<br>
`xxxxxxx`を自身のGitHubユーザー名に置き換えてください。

```
cd ~/notice_shoheiOhtani_homeruns
sed -i -e "s/ikayarou/xxxxxxx/g" buildspec.yml
sed -i -e "s/ikayarou/xxxxxxx/g" Dockerfile
sed -i -e "s/ikayarou/xxxxxxx/g" run.sh
git add .
git commit -m "Changed GitHub username."
git push
```

### 2. CodeCommitのSSHキーを登録

自身のIAMユーザーの認証情報から`AWS CodeCommit の SSH キー`にSSHキーを登録し、SSHキーIDを取得します。

### 3. CodeCommitへソースコードをPush

`notice_shoheiOhtani_homeruns`リポジトリ(名称固定)を作成し`master`ブランチに最新のコードをPushします。

```
git remote add prod ssh://APK123456789012xxxxx@git-codecommit.ap-northeast-1.amazonaws.com/v1/repos/notice_shoheiOhtani_homeruns
git push prod master
```

### 4. ECR への Docker Image の Push

```
docker build -t notice-ohtani-homeruns .
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com
docker tag notice-ohtani-homeruns:latest 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
```

### 5. AWS Batch の作成

`手順4`でECRにPushしたDocke Imageを利用する設定内容にて、AWS Batchを作成します。<br>
事前に対象パブリックサブネットにて、`パブリック IPv4 アドレスを自動割り当て`を有効化しておきます。

`コンピューティング環境`の設定については、以下にご注意ください。

| 項目 | 説明 | サンプル値 |
| --- | --- | --- |
| コンピューティング環境のタイプ | Fargateを使用するため | マネージド型 |
| プロビジョニングモデル | 同上 | Fargate |
| サブネット | パブリックサブネットで安く済ませるため | パブリックサブネット |

`ジョブキュー`は上記のコンピューティング環境を指定します。

`ジョブ定義`の設定については、以下にご注意ください。

| 項目 | 説明 | サンプル値 |
| --- | --- | --- |
| 実行タイムアウト | 実行時間が1分を超えるため | 120 |
| イメージ | 手順4でPushしたイメージ | 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest |
| コマンド | `xxxxxxx`はGitHubユーザー名 | /bin/bash /opt/xxxxxxx/run.sh |
| ジョブロール | CodeCommit、SSM、KMSの権限 | 面倒だったので PowerUser 権限を付与しちゃいました |
| 実行ロール | CodeCommit、SSM、KMSの権限 | 面倒だったので PowerUser 権限を付与しちゃいました |
| 環境変数の設定 | タイムゾーン | TZ: Asia/Tokyo |
| パブリックIPを割り当て | NGWなしでインターネット接続するため | ENABLED |

### 6. EventBridgeの設定

EventBridge Ruleから`手順5`で作成した`バッチジョブのキュー`を起動するように設定します。<br>
`0/5 * ? * * *` では、5分毎に起動するように設定しています。

## CI/CD

続き