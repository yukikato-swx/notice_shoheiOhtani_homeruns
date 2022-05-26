import time

import boto3
import selenium
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from slack_sdk import WebClient

from models.mlb_hitter import MlbHitter


ssm = boto3.client('ssm', region_name='ap-northeast-1')
# 返り値がパラメーター名のアルファベット順にNames(list)に格納されるため注意
ssm_response = ssm.get_parameters(
    Names = [
        '/shohei_ohtani_bot/current_season_row',
        '/shohei_ohtani_bot/current_season_year',
        '/shohei_ohtani_bot/slack_bot_token',
        '/shohei_ohtani_bot/slack_channel'
        ],
    WithDecryption = True
    )
row = ssm_response['Parameters'][0]['Value']
year = ssm_response['Parameters'][1]['Value']
slack_bot_token = ssm_response['Parameters'][2]['Value']
slack_channel = ssm_response['Parameters'][3]['Value']

# Seleniumセットアップ
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1680,1080')
browser = selenium.webdriver.Chrome(ChromeDriverManager().install(), options=options)
browser.delete_all_cookies()


def main():
    browser.get('https://www.mlb.com/player/shohei-ohtani-660271')

    # <section class="statistics"> に含まれる <button data-type="hitting"> ボタンをクリック
    button = filter_elements(
        browser.find_elements_by_xpath("//button[@data-type='hitting']"),
        'class',
        'statistics'
    )
    browser.execute_script('arguments[0].click();', button)
    time.sleep(3)   # 描画を3秒間待ちます

    # <div id="careerTable"> に含まれる <td class="col-10.row-x"> を標準出力
    scopes = [
        {'year': year, 'row': row},
    ]
#    scopes = [
#        {'year': '2018', 'row': 'row-0'},
#        {'year': '2019', 'row': 'row-1'},
#        {'year': '2020', 'row': 'row-2'},
#        {'year': '2021', 'row': 'row-3'},
#    ]
    for scope in scopes:
        stats = filter_elements(
            browser.find_elements_by_class_name("col-10.%s" % scope['row']),
            'id',
            'careerTable'
        )
        current_homerun_counts = stats.text
#        print("%s: %s" % (scope['year'], stats.text))

    # ブラウザの終了
    browser.close()
    browser.quit()

    # Slackセットアップ
    client = WebClient(token=slack_bot_token)
    text = ("速報： :tada:大谷翔平が第 " + current_homerun_counts + " 号ホームランを打ちました！！！:tada:")

    # DynamoDBの操作 + slack通知
    season_homeruns = int(current_homerun_counts)
    if not MlbHitter.exists():
        # wait=trueでDynamoDBの作成完了まで待機
        MlbHitter.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
    diff_homeruns(year, season_homeruns, client, text)


def filter_elements(elements, parent_key, parent_value):
    for element in elements:
        path = './..'

        while True:
            target = element.find_element_by_xpath(path)
            if target.tag_name == 'html':
                break
            elif target.get_attribute(parent_key) == parent_value:
                return element
            else:
                path += '/..'

    return None


def diff_homeruns(year, season_homeruns, client, text):
    try:
        for shohei in MlbHitter.query(year):
            query_result = int(shohei.season_homeruns)
        if season_homeruns > query_result:
            update_shohei(year, str(season_homeruns))
            slack_message(client, text)
    except UnboundLocalError: # DynamoDBのItemが未登録の場合に発生
            update_shohei(year, str(season_homeruns))


def update_shohei(year, season_homeruns):
    shohei = MlbHitter()
    shohei.year = year
    shohei.season_homeruns = season_homeruns
    shohei.save()


def slack_message(client, text):
    response = client.chat_postMessage(
        channel=slack_channel,
        text=text
    )


if __name__ == "__main__":
    main()
