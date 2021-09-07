import json
import os

from bs4 import BeautifulSoup
from pynamodb.models import Model
import requests
from pynamodb.attributes import UnicodeAttribute
from slack_sdk import WebClient

def lambda_handler(event, context):

    load_url = "https://baseball.yahoo.co.jp/mlb/teams/player/pitcher/727378"
    html = requests.get(load_url)
    soup = BeautifulSoup(html.content, "html.parser")

    years_stats = {}
    list1 = []

    for player in soup.find_all(class_="yjSMTseasonsscore"):
        for table in player.find_all("tr"):
            list1.append(table)

    del list1[0:4]

    index = []

    for index_raw in list1[0].find_all("th"):
        index.append(index_raw.text)

    del index[0]

    for value1 in list1[1:]:
        value = []
        for value2 in value1.find_all("td"):
            value.append(value2.text)
        # print (value)

        stats = {}
        for i in range(0,len(index)):
            stats[index[i]] = value[i]

        # print (stats)

        years_stats[value1.find("th").text] = stats

    #print (years_stats)
    #print ("本塁打数: " + years_stats["2021"]["本塁打"])

    slack_token = os.environ['SLACK_BOT_TOKEN']
    client = WebClient(token=slack_token)

    channel = os.environ['SLACK_CHANNEL']
    text = ("速報： :tada:大谷翔平が第 " + years_stats["2021"]["本塁打"] + " 号ホームランを打ちました！！！:tada:")

    def slack_message(client, text):
        response = client.chat_postMessage(
            channel=channel,
            text=text
        )

    class OhtaniModel(Model):
        """
        Shohei Ohtani Homeruns
        """
        class Meta:
            table_name = "shoheiOhtaniHomeruns"
            region = os.environ['REGION']
        year = UnicodeAttribute(hash_key=True)
        season_homeruns = UnicodeAttribute(null=True)

    if not OhtaniModel.exists():
        OhtaniModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    def update_shohei(year, season_homeruns):
        shohei = OhtaniModel()
        shohei.year = year
        shohei.season_homeruns = season_homeruns
        shohei.save()

    year = "2021"
    season_homeruns = int(years_stats["2021"]["本塁打"])

    def diff_homeruns(year, season_homeruns):
        for shohei in OhtaniModel.query(year):
            query_result = int(shohei.season_homeruns)
        if season_homeruns > query_result:
            update_shohei(year, str(season_homeruns))
            slack_message(client, text)

    diff_homeruns(year, season_homeruns)

    return {
        'statusCode': 200,
        'body': json.dumps('End Shohei!')
    }