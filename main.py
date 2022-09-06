from flask import Flask, request
import math, datetime
import pandas as pd

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

BANKS = ['yuucho.csv', 'SMBC.csv', 'UFJ.csv'] # 直営リスト
CONVENIENT_ATM = ['seven_eleven.csv', 'lawson.csv', 'family_mart.csv'] # コンビニATMは手数料かかると思われ
CODES = {'yuucho.csv':'9900', 'SMBC.csv':'0009', 'UFJ.csv':'0005'}

# pole_radius = 6356752.314245                  # 極半径
# equator_radius = 6378137.0                    # 赤道半径
# e2 = (math.pow(equator_radius, 2) - math.pow(pole_radius, 2)) \
#         / math.pow(equator_radius, 2)  # 第一離心率^2

@app.route('/', methods=["GET"])
def test():
    return '<p>hello world</p>'

@app.route('/getATMs', methods=["POST"])
def main():
    nearATMs = []
    req = request.json
    longitude = req.get("longitude")
    latitude = req.get("latitude")
    minute = req.get('minute') # 徒歩何分以内か指定, 80m/min
    minute = int(minute)
    weekday = datetime.date.today().weekday() # 0-4: weekdays, 5:saturday, 6:holidays
    for bank in BANKS+CONVENIENT_ATM:
        file = pd.read_csv(bank, encoding='utf-8')
        names = file['name'].tolist()
        columns = file.columns
        lngs = file[columns[-2]].tolist()
        lats = file[columns[-1]].tolist()
        start_times = file[columns[3]].tolist()
        end_times = file[columns[4]].tolist()
        ATM_type = 0
        if bank in CONVENIENT_ATM:
            ATM_type = 1
        if weekday == 5: # saturday
            start_times = file[columns[5]].tolist()
            end_times = file[columns[6]].tolist()
        elif weekday == 6:
            start_times = file[columns[7]].tolist()
            end_times = file[columns[8]].tolist()
        for i in range(len(lngs)):
            # これは別の緯度経度距離計算方法
            # lat_average = (float(latitude)+float(lats[i]))/2
            # W = math.sqrt(1- e2 * math.pow(math.sin(lat_average), 2))

            # M = equator_radius * (1 - e2) / math.pow(W, 3) # 子午線曲率半径

            # N = equator_radius / W
            # distance = ((float(latitude)-float(lats[i]))*M)**2 + ((float(longitude)-float(lngs[i]))*N*math.cos(lat_average))**2
            distance = math.sqrt((91000*(float(lngs[i])-float(longitude)))**2 + (111000*(float(lats[i])-float(latitude)))**2)
            if distance <= (80*minute):
                nearATMs.append({'bank_name':bank[:-4], 'address':file[columns[2]].tolist()[i], 'longitude':lngs[i],
                                    'latitude':lats[i], 'name':names[i], 'start_time':start_times[i], 'end_time':end_times[i],
                                    'ATM_type':ATM_type, 'commission':file[columns[9]].tolist()[i]})
    res = {'res':nearATMs}
    return res

@app.route('/filterATMs', methods=['POST'])
def filter():
    req = request.json
    code = req.get('code') # どの銀行か
    weekday = req.get('weekday') # 何曜日か 0-4: weekdays, 5:saturday, 6:holidays
    time = req.get('time') # 営業中か?(今日か明日か??何の絞り込みか不明)、実装は放置しておく
    atm_type = req.get('ATM_type') # 0:直営, 1:コンビニ
    longitude = req.get("longitude")
    latitude = req.get("latitude")
    minute = req.get('minute') # 徒歩何分以内か指定, 80m/minとしているが歩幅の大きさ調整できても良さそう
    minute = int(minute)
    nearATMs = []
    if atm_type == 0:
        for (k, v) in CODES.items():
            if code == v:
                file = pd.read_csv(k, encoding='utf-8')
                names = file['name'].tolist()
                columns = file.columns
                lngs = file[columns[-2]].tolist()
                lats = file[columns[-1]].tolist()
                start_times = file[columns[3]].tolist()
                end_times = file[columns[4]].tolist()
                if weekday == 5: # saturday
                    start_times = file[columns[5]].tolist()
                    end_times = file[columns[6]].tolist()
                elif weekday == 6:
                    start_times = file[columns[7]].tolist()
                    end_times = file[columns[8]].tolist()
                for i in range(len(lngs)):
                    distance = math.sqrt((91000*(float(lngs[i])-float(longitude)))**2 + (111000*(float(lats[i])-float(latitude)))**2)
                    if distance <= (80*minute):
                        nearATMs.append({'code':code, 'address':file[columns[2]].tolist()[i], 'longitude':lngs[i],
                                            'latitude':lats[i], 'name':names[i], 'start_time':start_times[i], 'end_time':end_times[i]})
    elif atm_type == 1:
        for bank in CONVENIENT_ATM:
            file = pd.read_csv(bank, encoding='utf-8')
            names = file['name'].tolist()
            columns = file.columns
            lngs = file[columns[-2]].tolist()
            lats = file[columns[-1]].tolist()
            start_times = file[columns[3]].tolist()
            end_times = file[columns[4]].tolist()
            if weekday == 5: # saturday
                start_times = file[columns[5]].tolist()
                end_times = file[columns[6]].tolist()
            elif weekday == 6:
                start_times = file[columns[7]].tolist()
                end_times = file[columns[8]].tolist()
            for i in range(len(lngs)):
                distance = math.sqrt((91000*(float(lngs[i])-float(longitude)))**2 + (111000*(float(lats[i])-float(latitude)))**2)
                if distance <= (80*minute):
                    nearATMs.append({'code':CODES[bank], 'address':file[columns[2]].tolist()[i], 'longitude':lngs[i],
                                        'latitude':lats[i], 'name':names[i], 'start_time':start_times[i], 'end_time':end_times[i]})
    res = {'res':nearATMs}
    return res

if __name__ == "__main__":
    app.run(debug=True)
