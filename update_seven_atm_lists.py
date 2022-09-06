"""
セブン銀行一覧のクローリング
https://map.japanpost.jp/p/search/search.htm?&cond40=1&cond200=1&&&his=sa&&type=ShopA&area1=26&slogflg=1&areaptn=1&selnm=%B5%FE%C5%D4%C9%DC
ここから対象の市をクリックした後、そのURLをURLsに書き換える
"""
import pandas as pd
import requests, csv, mojimoji
from bs4 import BeautifulSoup

URLs = [
    'https://pkg.navitime.co.jp/sevenbank/spot/list?page=1&c_d1=1&address=26103',
    'https://pkg.navitime.co.jp/sevenbank/spot/list?page=2&c_d1=1&address=26103',
    'https://pkg.navitime.co.jp/sevenbank/spot/list?page=3&c_d1=1&address=26103'
]
file = pd.read_csv('seven_eleven.csv')
names = file['name'].tolist()
f = open('seven_eleven.csv','a')
writer = csv.writer(f)
names = set(names)
for URL in URLs:
    re = requests.get(URL)
    soup = BeautifulSoup(re.text, 'html.parser')
    mat = []
    banks = []
    tbody = soup.select_one('#w_1_searchresult_1_1_tbody')
    trs = tbody.find_all('td')
    pointer = 0
    for tr in trs:
        pointer += 1
        if pointer == 1:
            name = tr.find_all('a')[0].text
            banks.append(name)
            banks[-1] = banks[-1].replace('\t', '')
            banks[-1] = banks[-1].replace('\n', '')
            banks[-1] = banks[-1].replace(' ', '')
            banks[-1] = banks[-1].replace('　', '')
        elif pointer == 4:
            ad = mojimoji.zen_to_han(tr.text)
            banks.append(ad)
            banks[-1] = banks[-1].replace('\t', '')
            banks[-1] = banks[-1].replace('\n', '')
            banks[-1] = banks[-1].replace(' ', '')
            banks[-1] = banks[-1].replace('　', '')
        elif pointer == 5:
            detail = tr.text
            if '24時間営業ではありません' in detail:
                banks.append('not 24 hours')
            elif '24時間' in detail:
                banks.append('24 hours')
            else:
                start_time = detail.split('-')[0]
                end_time = detail.split('-')[1].split('※')[0]
                banks.append(start_time+'-'+end_time)
            pointer = 0
            banks[-1] = banks[-1].replace('\t', '')
            banks[-1] = banks[-1].replace('\n', '')
            banks[-1] = banks[-1].replace(' ', '')
            banks[-1] = banks[-1].replace('　', '')
            mat.append(banks)
            banks = []
    for element in mat:
        line = []
        line += element[:2]
        if '-' in element[2]:
            line.append(element[2].split('-')[0])
            line.append(element[2].split('-')[1])
            line.append(element[2].split('-')[0])
            line.append(element[2].split('-')[1])
            line.append(element[2].split('-')[0])
            line.append(element[2].split('-')[1])
        elif '24hours' == element[2]:
            line.append('0:00')
            line.append('24:00')
            line.append('0:00')
            line.append('24:00')
            line.append('0:00')
            line.append('24:00')
        else:
            line.append('not 24hour')
            line.append('not 24hour')
            line.append('not 24hour')
            line.append('not 24hour')
            line.append('not 24hour')
            line.append('not 24hour')
        line.append(110)
        line.append('')
        line.append('')
        writer.writerow(line)
