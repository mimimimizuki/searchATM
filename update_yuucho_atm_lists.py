"""
ゆうちょ銀行一覧のクローリング
https://map.japanpost.jp/p/search/search.htm?&cond40=1&cond200=1&&&his=sa&&type=ShopA&area1=26&slogflg=1&areaptn=1&selnm=%B5%FE%C5%D4%C9%DC
ここから対象の市をクリックした後、そのURLをURLsに書き換える
"""
from bs4 import BeautifulSoup
import requests
import csv, mojimoji
import pandas as pd

URLs = [
    'https://map.japanpost.jp/p/search/search.htm?type=ShopA&area1=26&area2=%A4%AD%A4%E8%A4%A6%A4%C8%A4%B7%A4%E4%A4%DE%A4%B7%A4%CA%A4%AF%23%23%B5%FE%C5%D4%BB%D4%BB%B3%B2%CA%B6%E8&cond1=3&page=0&his=sa1%2Csa2&search=&cond200=1',
    'https://map.japanpost.jp/p/search/search.htm?type=ShopA&area1=26&area2=%A4%AD%A4%E8%A4%A6%A4%C8%A4%B7%A4%D2%A4%AC%A4%B7%A4%E4%A4%DE%A4%AF%23%23%B5%FE%C5%D4%BB%D4%C5%EC%BB%B3%B6%E8&cond1=3&page=0&his=sa1%2Csa2&search=&cond200=1',
    'https://map.japanpost.jp/p/search/search.htm?type=ShopA&area1=26&area2=%A4%AD%A4%E8%A4%A6%A4%C8%A4%B7%A4%D2%A4%AC%A4%B7%A4%E4%A4%DE%A4%AF%23%23%B5%FE%C5%D4%BB%D4%C5%EC%BB%B3%B6%E8&cond1=3&page=0&his=sa1%2Csa2&search=&cond200=1',
    'https://map.japanpost.jp/p/search/search.htm?type=ShopA&area1=26&area2=%A4%AD%A4%E8%A4%A6%A4%C8%A4%B7%A4%AB%A4%DF%A4%AE%A4%E8%A4%A6%A4%AF%23%23%B5%FE%C5%D4%BB%D4%BE%E5%B5%FE%B6%E8&cond1=3&page=0&his=sa1%2Csa2&search=&cond200=1',
    'https://map.japanpost.jp/p/search/search.htm?type=ShopA&area1=26&area2=%A4%AD%A4%E8%A4%A6%A4%C8%A4%B7%A4%DF%A4%CA%A4%DF%A4%AF%23%23%B5%FE%C5%D4%BB%D4%C6%EE%B6%E8&cond1=3&page=0&his=sa1%2Csa2&search=&cond200=1',
    'https://map.japanpost.jp/p/search/search.htm?type=ShopA&area1=26&area2=%A4%AD%A4%E8%A4%A6%A4%C8%A4%B7%A4%CB%A4%B7%A4%AD%A4%E8%A4%A6%A4%AF%23%23%B5%FE%C5%D4%BB%D4%C0%BE%B5%FE%B6%E8&cond1=3&page=0&his=sa1%2Csa2&search=&cond200=1',
    'https://map.japanpost.jp/p/search/search.htm?type=ShopA&area1=26&area2=%A4%AD%A4%E8%A4%A6%A4%C8%A4%B7%A4%CB%A4%B7%A4%AD%A4%E8%A4%A6%A4%AF%23%23%B5%FE%C5%D4%BB%D4%C0%BE%B5%FE%B6%E8&cond1=3&page=0&his=sa1%2Csa2&search=&cond200=1,'
    ]
file = pd.read_csv('yuucho.csv')
names = file['name'].tolist()
f = open('yuucho.csv','a')
writer = csv.writer(f)
names = set(names)
for URL in URLs:
    re = requests.get(URL)
    soup = BeautifulSoup(re.text, 'html.parser')

    table = soup.select_one('#searchShopListData')

    r = []
    mat = []
    tds = table.find_all('td')
    flg2 = False
    flg3 = False

    bank_urls = []
    for t in tds:
        if '次へ' in t.text or '前へ' in t.text:
            continue
        if len(t.find_all('a')) == 1: # 郵便局の名前
            r.append(t.text)
            r[-1] = r[-1].replace('\t', '')
            r[-1] = r[-1].replace('\n', '')
            r[-1] = r[-1].replace('\xa0', '')
            # r[-1] = r[-1].replace('\u3000', '')
            bank_urls.append(t.find('a').get('href'))
        else:
            if flg2: # 郵便局の住所
                ad = mojimoji.zen_to_han(t.text)
                r.append(ad)
                flg2 = False
                r[-1] = r[-1].replace('\t', '')
                r[-1] = r[-1].replace('\n', '')
                r[-1] = r[-1].replace('〒', '')
                r[-1] = r[-1][8:]
            elif flg3: # ATMの有無
                imgs = t.find_all('img', src='https://map.japanpost.jp/p/search/company/search/images/icon_atm.gif')
                imgs.append(t.find_all('img', src='https://map.japanpost.jp/p/search/company/search/images/icon_atm_s.gif'))
                flg3 = False
                if len(imgs) >= 1:
                    r.append('True')
                else:
                    r.append('False')
            elif len(t.find_all('img')) == 0:
                flg2 = True
            elif len(t.find_all('img')) != 0:
                flg3 = True
    print(r)
    print(len(r), len(bank_urls))
    assert len(r)/3 == len(bank_urls)
    mat = []

    for i in range(0, len(r), 3):
        bank = [r[i], r[i+1], r[i+2]]
        mat.append(bank)

    for (i, bank_url) in enumerate(bank_urls):
        r = requests.get(bank_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.select_one('.tableTypeA')
        trs = table.find_all('tr')
        for e in trs:
            if 'ATM' in e.text:
                tr = e # ATM
                tds = tr.find_all('td') # length is 3: weekdays, saturday, holidays
                if 'お取り扱いしません' not in tds[0].text:
                    start_time, end_time = tds[0].text.split('〜')
                    mat[i].append(start_time)
                    mat[i].append(end_time)
                else:
                    mat[i].append('-')
                    mat[i].append('-')
                if 'お取り扱いしません' not in tds[1].text:
                    start_time, end_time = tds[1].text.split('〜')
                    mat[i].append(start_time)
                    mat[i].append(end_time)
                else:
                    mat[i].append('-')
                    mat[i].append('-')
                if 'お取り扱いしません' not in tds[2].text:
                    start_time, end_time = tds[2].text.split('〜')
                    mat[i].append(start_time)
                    mat[i].append(end_time)
                else:
                    mat[i].append('-')
                    mat[i].append('-')
                mat[i].append(0)
                break

    res = []
    for element in mat:
        element[3] = element[3].replace('\t', '')
        element[3] = element[3].replace('\n', '')
        element[4] = element[4].replace('\t', '')
        element[4] = element[4].replace('\n', '')
        element[5] = element[5].replace('\t', '')
        element[5] = element[5].replace('\n', '')
        element[6] = element[6].replace('\t', '')
        element[6] = element[6].replace('\n', '')
        element[7] = element[7].replace('\t', '')
        element[7] = element[7].replace('\n', '')
        element[8] = element[8].replace('\t', '')
        element[8] = element[8].replace('\n', '')
        if element[2] == 'True':
            res.append(element[:2]+element[3:]+['']+['']) # 緯度経度の部分を残しておく
        if element[0] not in names:
            writer.writerow(element[:2]+element[3:]+['']+['']) # 緯度経度の部分を残しておく
