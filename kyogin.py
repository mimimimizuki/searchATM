import requests
from bs4 import BeautifulSoup
import csv
import re
import subprocess


def add_hour(day, day_list, hour, row):
    if day in day_list:
        h = hour[day_list == day]
        hour_str = h.find("span").next_sibling.strip()
        hour_sp = re.split("：|:", hour_str)
        start_h = hour_sp[0]
        start_m = hour_sp[1].split("～")[0]
        end_h = hour_sp[1].split("～")[1]
        end_m = hour_sp[2]
        row.append(f"{start_h}:{start_m}")
        row.append(f"{end_h}:{end_m}")
    else:
        row.append("-")
        row.append("-")


def get_rows(load_url):
    html = requests.get(load_url)
    soup = BeautifulSoup(html.content, "html.parser")
    next_tag = soup.find(id="m_nextpage_link")
    if next_tag:
        next_url = next_tag.get("href")

    row = []
    topic = soup.find(class_="MapiTable")
    for i, element in enumerate(topic.find_all("tr")):
        if i % 2 == 0:
            a_tag = element.find("a")
            row.append(a_tag.text)
        else:
            info = element.select("dl.MapiClearfix")
            info_list = list(map(lambda x: x.find("dt").text, info))
            if "ＡＴＭご利用時間：" not in info_list:
                row = []
                continue
            for j in info:
                if j.find("dt").text == "住所：":
                    if j.find("dd").text[0] == "〒":
                        row.append(j.find("dd").text[10:])
                    else:
                        row.append(j.find("dd").text[1:])
                elif j.find("dt").text == "ＡＴＭご利用時間：":
                    hour = j.find("dd").find_all("li")
                    day_list = list(map(lambda x: x.find("span").text, hour))
                    add_hour("平日/", day_list, hour, row)
                    add_hour("土曜日/", day_list, hour, row)
                    add_hour("日・祝日/", day_list, hour, row)
            row.append(110)
            rows.append(row)
            row = []
    if next_tag:
        get_rows(f"https://sasp.mapion.co.jp/{next_url}")


f = open("kyogin2.csv", "w")
writer = csv.writer(f)
load_url = f"https://sasp.mapion.co.jp/b/kyotobank/attr/"
rows = []
get_rows(load_url)
print(len(rows))
writer.writerow(
    [
        "",
        "name",
        "address",
        "start_time",
        "end_time",
        "start_time_saturday",
        "end_time_saturday",
        "start_time_holiday",
        "end_time_holiday",
        "fee",
    ]
)
for i, r in enumerate(rows):
    writer.writerow([i] + r)

subprocess.run(["python", "geo.py", "kyogin2.csv"])

with open("./output.csv") as f:
    reader = csv.reader(f)
    O = [row for row in reader]

f = open("kyogin2.csv", "w")
writer = csv.writer(f)
writer.writerow(
    [
        "",
        "name",
        "address",
        "start_time",
        "end_time",
        "start_time_saturday",
        "end_time_saturday",
        "start_time_holiday",
        "end_time_holiday",
        "fee",
        "longitude",
        "latitude",
    ]
)

for o in O[1:]:
    if o[-2:] == ["", ""]:
        load_url = f"https://www.geocoding.jp/?q={o[2]}"
        html = requests.get(load_url)
        soup = BeautifulSoup(html.content, "html.parser")
        topic = soup.find(class_="nowrap")
        b_tag = topic.find_all("b")
        print([b_tag[1].text, b_tag[0].text])
        writer.writerow(o + [b_tag[1].text, b_tag[0].text])
    else:
        writer.writerow(o)
