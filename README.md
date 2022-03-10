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

### 4. ECRへのDocker ImageのPush

```
docker build -t notice-ohtani-homeruns .
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com
docker tag notice-ohtani-homeruns:latest 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/notice-ohtani-homeruns:latest
```

### 5. AWS Batchの作成

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
| vCPU | 最低2以上 | 2.0 |
| ジョブロール | CodeCommit、SSM、KMSの権限 | 面倒だったので PowerUser 権限を付与しちゃいました |
| 実行ロール | CodeCommit、SSM、KMSの権限 | 面倒だったので PowerUser 権限を付与しちゃいました |
| 環境変数の設定 | タイムゾーン | TZ: Asia/Tokyo |
| パブリックIPを割り当て | NGWなしでインターネット接続するため | ENABLED |

### 6. EventBridgeの設定

EventBridge Ruleから`手順5`で作成した`バッチジョブのキュー`を起動するように設定します。<br>
`0/5 * ? * * *` では、5分毎に起動するように設定しています。

## CI/CD

### 1. Secretsの設定

GitHubの更新を行ったらCodeCommit上へミラーリングされるように設定します。<br>
ミラーリング用の設定ファイル`.github/workflows/main.yml`がすでに存在するため、CodeCommit接続用のSecretsを作成します。

リポジトリ`notice_shoheiOhtani_homeruns`のHomeから`Settings`、`Secrets`、`Actions`と選択します。<br>
`New repository secret`から以下のSecretsを作成します。

| Name | Value |
| --- | --- |
| CODECOMMIT_SSH_PRIVATE_KEY | `CodeCommitのSSHキーを登録`に使用した秘密鍵の中身 |
| CODECOMMIT_SSH_PRIVATE_KEY_ID | `CodeCommitのSSHキーを登録`で取得したSSHキーID |

### 2. CodeBuildの作成

Dockerイメージをビルドするためのビルドプロジェクトを作成します。

設定については、以下にご注意ください。

| 項目 | 説明 | サンプル値 |
| --- | --- | --- |
| ソースプロバイダ | CodeCommitと連携するため | AWS CodeCommit |
| リポジトリ | 大谷翔平Bot用のCodeCommitリポジトリを選択 | notice_shoheiOhtani_homeruns |
| ブランチ | masterブランチを使用 | master |
| 環境イメージ | ビルド環境はAWSが提供するイメージを使用 | マネージド型イメージ |
| オペレーティングシステム | 使い慣れているOSを使用 | Amazon Linux 2 |
| イメージ | 最新イメージを使用 | aws/codebuild/amazonlinux2-x86_64-standard:3.0 |
| 特権付与 | CodeBuild上でDockerを使用する場合は必須 | 有効 |
| サービスロール | すでにあれば既存のものでも構いません | 新しいサービスロール |

作成後、`サービスロール`に`PowerUserAccess`権限を付与してください。<br>
CodeBuild上でパラメータストア、ECRを使用するために必要です。

### 3. CodePipelineの作成

CI/CDの視認性や運用管理を向上させるためにCodePipelineのパイプラインを作成します。

設定については、以下にご注意ください。

| 項目 | 説明 | サンプル値 |
| --- | --- | --- |
| ソースプロバイダ | CodeCommitと連携するため | AWS CodeCommit |
| リポジトリ | 大谷翔平Bot用のCodeCommitリポジトリを選択 | notice_shoheiOhtani_homeruns |
| ブランチ | masterブランチを使用 | master |
| プロバイダーを構築する | Codebuildと連携するため | AWS CodeBuild |
| プロジェクト名 | Codebuildに作成したプロジェクトを選択 | shohei-ohtani-bot |
| デプロイプロバイダー | CodebuildでDockerイメージをビルドしてECRにプッシュすれば完了となるため不要 | \- |

### 4. CI/CDの確認

GitHubを更新してCI/CDが動作していることを確認します。<br>
開発環境のEC2上で`handler.py`のコードを一部変更し、開発環境で単体テストを行います。

```
cd ~/notice_shoheiOhtani_homeruns
sed -i -e "s/大谷/柿崎/g" handler.py
pipenv shell
PATH=$PATH:`chromedriver-path` python handler.py
```

Slack上に`柿崎翔平`が出現したら単体テストに成功です。<br>
開発環境上でのテストに問題がなかった場合は、GitHubを更新します。

```
git add .
git commit -m "Changed Ohtani."
git push
```

`git push`に成功したら、AWS CodePipelineのパイプラインが動作し、正常に実行されていることを確認してください。<br>
※完了までに少し時間がかかります。

パイプラインまで正常に完了するとECR上のDockerイメージが更新されています。<br>
この状態でAWS Batchのジョブ定義から`新しいジョブを送信`します。<br>
Slack上に`柿崎翔平`が出現したら単体テストに成功です。

`大谷翔平`に戻したい場合は、開発環境で以下のコマンドを実行してください。

```
cd ~/notice_shoheiOhtani_homeruns
sed -i -e "s/柿崎/大谷/g" handler.py
git add .
git commit -m "Changed Kakizaki."
git push
```

---