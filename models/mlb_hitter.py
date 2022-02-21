from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute


class MlbHitter(Model):
    class Meta:
        table_name = 'shoheiOhtaniHomeruns'
        region = 'ap-northeast-1'
    year = UnicodeAttribute(hash_key=True)
    season_homeruns = UnicodeAttribute(null=True)