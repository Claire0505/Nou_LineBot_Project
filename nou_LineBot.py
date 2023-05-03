from flask import Flask,request, abort
app = Flask(__name__)

import requests
import bs4
from linebot.exceptions import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime

# Line Channel access token
line_bot_api = LineBotApi('你的 Line Channel access token')
# Line Channel secret
handler = WebhookHandler('你的 Line Channel secret')

# 設定 User-Agent 避免被網站擋掉
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# 指定在 /callback 通道上接收訊息，且方法是 POST
# callback()是為了要檢查連線是否正常
@app.route("/callback", methods=['POST'])
def callback(callback=None):
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 台灣銀行-每日金價
gold_url = 'https://rate.bot.com.tw/gold?Lang=zh-TW'
# 台灣銀行-每日匯率
exchange_url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'

# 抓取每日金價
gold_res = requests.get(gold_url)
gold_soup = bs4.BeautifulSoup(gold_res.text, 'html.parser')
gold_table = gold_soup.find('table', {'title': '新臺幣黃金牌價'}).find('tbody')
gold_time_element = gold_soup.find('div', {'class': 'pull-left trailer text-info'}).text.strip()

# 金價掛牌時間
def get_gold_price():
    message = ''
    for tr in gold_table.find_all('tr'):
        # 抓取商品名稱和價格
        name = tr.find('td', {'class': 'text-center'}).text.strip()
        price = tr.find('td', {'class': 'text-right'}).text.strip()
        #print(f'{name}: {price.split()[0]}')
        message += f'{name}: {price.split()[0]}\n'
        
    return f'黃金存摺 每 1 公克 (新臺幣元)\n{gold_time_element}\n{message}'

# 抓取匯率
exchange_rate_res = requests.get(exchange_url, headers)
exchange_rate_soup = bs4.BeautifulSoup(exchange_rate_res.text, 'html.parser')

def get_exchange_rate(currency):
    message = ""
    # 牌價最新掛牌時間
    rate_time_element = exchange_rate_soup.find('p', {'class': 'text-info'}).find('span', {'class': 'time'}).text.strip()
    exchange_rate_table = exchange_rate_soup.find('table', {'title': '牌告匯率'}).find('tbody')
    # 定義支援的幣別
    supported_currencies = ['USD', 'JPY', 'HKD','GBP','AUD','CAD', 'SGD','CHF','ZAR','SEK',
                            'NZD', 'THB', 'PHP', 'IDR','EUR','KRW', 'VND','MYR','CNY']  

    if currency not in supported_currencies:
        return f"很抱歉，找不到 {currency} 的匯率資料。"

    for tr in exchange_rate_table.find_all('tr'):
        # 抓取幣別、現金買入匯率、現金賣出匯率、即期買入匯率、即期賣出匯率
        currency_td = tr.find('td', {'class': 'currency phone-small-font'})

        if currency_td and currency in currency_td.text.strip():
            currency_id = tr.find('div', {'class': 'visible-phone print_hide'}).text.strip()
            cash_buy_rate = tr.find('td', {'data-table': '本行現金買入'}).text.strip()
            cash_sell_rate = tr.find('td', {'data-table': '本行現金賣出'}).text.strip()
            spot_buy_rate = tr.find('td', {'data-table': '本行即期買入'}).text.strip()
            spot_sell_rate = tr.find('td', {'data-table': '本行即期賣出'}).text.strip()
            # 找到符合幣別的匯率就跳出迴圈
            break
    else:
        return f"很抱歉，找不到 {currency} 的匯率資料。"

    # message = f"臺灣銀行牌告匯率:{rate_time_element}\n{currency} 匯率資訊：\n現金買入 {cash_buy_rate}\n現金賣出 {cash_sell_rate}\n即期買入 {spot_buy_rate}\n即期賣出 {spot_sell_rate}"
    message = f"臺灣銀行牌告匯率:{rate_time_element}\n{currency_id} 匯率資訊：\n現金買入 {cash_buy_rate}\n現金賣出 {cash_sell_rate}\n即期買入 {spot_buy_rate}\n即期賣出 {spot_sell_rate}"
    return message


def get_delicacy_food(city):
    # 向愛食記網站發送請求，獲取縣市的餐廳資訊，取得最高人氣 
    # https://ifoodie.tw/explore/%E6%96%B0%E7%AB%B9%E5%B8%82/list?sortby=popular

    url = f'https://ifoodie.tw/explore/{city}/list?sortby=popular&opening=true'
    iFoodie_res = requests.get(url)
    soup = bs4.BeautifulSoup(iFoodie_res.text, 'html.parser')
    
    # 解析網頁內容，取得前五筆餐廳資訊
    restaurant_list = soup.find_all('div', {'class': 'jsx-1156793088 restaurant-info'})[:5]
    
    result = []
    message = ''
    
    for restaurant in restaurant_list:
        title = restaurant.find('a', {'class': 'jsx-1156793088 title-text'}).text.strip()
        rating = restaurant.find('div', {'class': 'jsx-2373119553 text'}).text.strip()
        address = restaurant.find('div', {'class': 'jsx-1156793088 address-row'}).text.strip()
        result.append({'title': title, 'rating': rating, 'address': address})
    
        # 將餐廳資訊整理成一個字串
        if len(result) > 0:
            message = f'【愛食記】推薦\n{city}的熱門美食餐廳資訊如下：\n\n'
            for r in result:
                message += f'餐廳名稱: {r["title"]}\n評價:{r["rating"]}\n地址:{r["address"]}\n\n'
        else:
            message = f'很抱歉，找不到 {city} 的餐廳資訊。'
    return message

# 每日星座
def get_today_star(star_text):
    message =""
    star_list = {
        "牡羊座": "0",
        "金牛座": "1",
        "雙子座": "2",
        "巨蟹座": "3",
        "獅子座": "4",
        "處女座": "5",
        "天秤座": "6",
        "天蠍座": "7",
        "射手座": "8",
        "摩羯座": "9",
        "水瓶座": "10",
        "雙魚座": "11"
    }

    if star_text in star_list:
        star_id = star_list[star_text]
        star_url = f'https://astro.click108.com.tw/daily_{star_id}.php?iAstro={star_id}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(star_url, headers=headers)
        response.encoding = 'utf-8'
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        # 取得今日運勢
        today_content = soup.find('div', {'class': 'TODAY_CONTENT'})
        today_text = today_content.get_text().strip()
        # 取得當前日期
        today = datetime.today().strftime('%m/%d')
        message =f'{today} {today_text}'
    else:
        message = "請輸入正確的星座名稱"
    return message

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg_text = event.message.text
    if msg_text.upper() == 'USD' or msg_text == '美金' or msg_text == '美':
        reply_text = get_exchange_rate('USD')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    elif msg_text.upper() == 'JPY' or msg_text == '日圓' or msg_text == '日':
        reply_text = get_exchange_rate('JPY')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    elif msg_text.upper() == 'HKD' or msg_text == '港幣' or msg_text == '港':
        reply_text = get_exchange_rate('HKD')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    elif msg_text.upper() == 'GBP' or msg_text == '英鎊' or msg_text == '英':
        reply_text = get_exchange_rate('GBP')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    elif msg_text.upper() == 'AUD' or msg_text == '澳幣' or msg_text == '澳':
        reply_text = get_exchange_rate('AUD')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    elif msg_text.upper() == 'CAD' or msg_text == '加拿大幣' or msg_text == '加':
        reply_text = get_exchange_rate('CAD')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    elif msg_text.upper() == 'SGD' or msg_text == '新加坡幣' or msg_text == '新':
        reply_text = get_exchange_rate('SGD')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'CHF' or msg_text == '瑞士法郎' or msg_text == '瑞士':
        reply_text = get_exchange_rate('CHF')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'ZAR' or msg_text == '南非幣' or msg_text == '南':
        reply_text = get_exchange_rate('ZAR')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'SEK' or msg_text == '瑞典幣' or msg_text == '瑞典':
        reply_text = get_exchange_rate('SEK')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'NZD' or msg_text == '紐元' or msg_text == '紐':
        reply_text = get_exchange_rate('NZD')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'THB' or msg_text == '泰幣' or msg_text == '泰':
        reply_text = get_exchange_rate('THB')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'PHP' or msg_text == '菲國比索' or msg_text == '比索':
        reply_text = get_exchange_rate('PHP')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    elif msg_text.upper() == 'IDR' or msg_text == '印尼幣' or msg_text == '印尼':
        reply_text = get_exchange_rate('IDR')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'EUR' or msg_text == '歐元' or msg_text == '歐':
        reply_text = get_exchange_rate('EUR')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'KRW' or msg_text == '韓元' or msg_text == '韓':
        reply_text = get_exchange_rate('KRW')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'VND' or msg_text == '越南盾' or msg_text == '越':
        reply_text = get_exchange_rate('VND')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'MYR' or msg_text == '馬來幣' or msg_text == '馬':
        reply_text = get_exchange_rate('MYR')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text.upper() == 'CNY' or msg_text == '人民幣' or msg_text == '人':
        reply_text = get_exchange_rate('CNY')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    elif msg_text == '黃金' or msg_text == '金':
        reply_text = get_gold_price()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    
    # 判斷是否為縣市名稱，如果是，則呼叫 get_delicacy_food 函式取得訊息
    # 使用[endswith] 表示以 "市" 或 "縣"結尾
    elif  msg_text.endswith('市') or msg_text.endswith('縣'):
        reply_text = get_delicacy_food(msg_text)
        line_bot_api.reply_message( event.reply_token,TextSendMessage(text=reply_text))
    
    elif  msg_text.endswith('座'):
        # 取得對應星座的今日運勢
        today_text = get_today_star(msg_text)
        # 回覆使用者取得的今日運勢
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=today_text))
        
    else:
        reply_text = '請輸入正確資料\n【即時匯率】和【即時金價】\n 請輸入關鍵字查詢\n(ex: 美，日，韓，金...)\n【美食推薦】\n 請輸入完整縣市名稱(ex:台中市)\n【每日星座】\n 請輸入完整星座名稱(ex:金牛座)'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=8080)
    app.run()
