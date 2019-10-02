from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import OrderedDict
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import json
import re

dthandler = lambda obj: (
    str(obj)
    if isinstance(obj, Decimal)
    or isinstance(obj, datetime.time)
    else None
)

#DB Connection
con = MongoClient('api.dimigo.life:27017')
con.admin.authenticate('dimigolife','dimigolife12#@')
db = con.life
col = db.dimibobs


html = urlopen("https://www.dimigo.hs.kr/index.php?mid=school_cafeteria&page=1")  

bsObject = BeautifulSoup(html, "html.parser") 
parse_url = []
re_date = re.compile('[0-9]*월 [0-9]*일')
re_meal = re.compile('조식|중식|석식')

meal_data = []

for link in bsObject.find_all('div', {'class':'scEllipsis'}):
    if re_date.match(link.select('a')[0].text):
        url = link.select('a')[0].get('href')
        parse_url.append(url)

for link in parse_url:
    html = urlopen(link)
    bsObject = BeautifulSoup(html, "html.parser")
    
    meal_json = OrderedDict()
    
    temp_date = bsObject.find('strong',{'class':'scClipboard'}).text.split(' ')
    meal_json['date']=bsObject.find('span',{'title':'등록일'}).text[1:5]+'-'+temp_date[0][0:temp_date[0].find('월')].zfill(2)+'-'+temp_date[1][0:temp_date[1].find('일')].zfill(2)
    for data in bsObject.find_all('p'):
        if re_meal.match(data.text):
            if '조식' in data.text:
                meal_json['breakfast']=data.text[data.text.find(': ')+2:]
            elif '중식' in data.text:
                meal_json['lunch']=data.text[data.text.find(': ')+2:]
            elif '석식' in data.text:
                meal_json['dinner']=data.text[data.text.find(': ')+2:]
    col.update({"date": meal_json['date']}, meal_json, upsert=True)
#     meal_data.append(meal_json)
# print(json.dumps(meal_data, ensure_ascii=False, indent="\t"))
