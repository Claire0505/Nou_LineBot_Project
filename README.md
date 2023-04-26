# 網路爬蟲與LINE BOT應用

## 摘要說明
這個程式是一個 Line 聊天機器人，提供使用者即時查詢台灣銀行的每日匯率與每日金價，還有美食推薦、每日星座，<br/>是一個多功能的聊天機器人，
程式會透過 Line 聊天機器人的 API 接收使用者傳來的訊息，再依照使用者傳來的訊息<br/>種類回傳相對應的訊息。
## 功能說明
- 即時匯率：
抓取台灣銀行即時匯率。
輸入貨幣代碼 "USD"、"美金" 或使用關鍵字 "美"，"日"，"港”..等即可獲得匯率資訊。
- 即時金價：
抓取台灣銀行-新臺幣黃金牌價 每日黃金牌價。
輸入關鍵字"黃金"，"金"，即可獲黃金牌價資訊。
- 美食推薦：
抓取愛食記各縣市的熱門美食餐廳(取得前五筆餐廳資訊。)
輸入縣市名稱 台北市、台中市，即可獲得當地熱門美食餐廳資訊。
- 每日星座：
抓取科技紫微網的每日星座運勢
輸入星座名稱 金牛座、水瓶座，即可獲得當日星座運勢。
## 開發環境
- 編輯器：Visual Studio Code
- 語言：Python 
- 框架：Flask
- 套件：requests、BeautifulSoup、linebot
## 執行或安裝步驟說明
1. 下載並安裝 Python 
2. 下載程式原始檔，GitHub Source Code 解壓縮至任意資料夾中
3. 安裝 Flask 套件：pip install Flask
4. 安裝 requests 套件：pip install requests
5. 安裝 BeautifulSoup 套件：pip install beautifulsoup4
6. 安裝 linebot 套件：pip install linebot
7. 建立 LINE BOT，取得 Channel access token 和 Channel secret
8. 將 Channel access token 和 Channel secret 填入程式碼中
9. 在終端機中進入程式檔案所在資料夾，執行程式：python  nou_linebot.py
## 程式碼撰寫相關說明
- 使用 Flask 框架建立 Web 應用程式
- 使用 requests、BeautifulSoup 套件進行網路爬蟲
- 使用 linebot 套件與 LINE Messaging API 進行 LINE BOT 開發
- 使用 ngrok 來測試 linebot 的 webhook 網址來接收資訊
- 使用 Google Cloud Functions 來部署程式並處理 linebot 的 webhook 請求 
```python
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
```

這段程式碼主要是在建立一個 Line 聊天機器人，讓使用者可以透過 Line 與機器人進行互動。
- line_bot_api = LineBotApi('你的 Line Channel access token')：設定 Line 聊天機器人的 Channel access token，用於透過 Line API 進行認證和授權。
- handler = WebhookHandler('你的 Line Channel secret')：設定 Line 聊天機器人的 Channel secret，用於進行加密和驗證訊息是否來自 Line 伺服器。
- headers = {...}：設定 User-Agent，用於模擬一個正常的瀏覽器請求，避免被網站擋掉。
- @app.route("/callback", methods=['POST'])：設定 Flask 網頁應用的路徑，指定在 /callback 通道上接收訊息，且方法是 POST。
- def callback():：定義回呼函數 callback()，處理接收到的訊息。
- signature = request.headers['X-Line-Signature']：從請求標頭中取得 X-Line-Signature，用於驗證訊息是否來自 Line 伺服器。
- body = request.get_data(as_text=True)：從請求中取得訊息主體，作為 Line 聊天機器人接收到的訊息。
- handler.handle(body, signature)：使用 Linebot SDK 中的 WebhookHandler，解析訊息並回傳相應的回覆。
- except InvalidSignatureError:：若驗證失敗，則回傳 HTTP 錯誤碼 400。return 'OK'：回傳 HTTP 響應碼 200，表示訊息已成功處理。

### 台灣銀行-每日匯率
```python
# 台灣銀行-每日匯率
exchange_url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
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

    message = f"臺灣銀行牌告匯率:{rate_time_element}\n{currency_id} 匯率資訊：\n現金買入 {cash_buy_rate}\n現金賣出 {cash_sell_rate}\n即期買入 {spot_buy_rate}\n即期賣出 {spot_sell_rate}"
    return message
```
```python
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
```

這段程式碼主要是抓取台灣銀行每日匯率資訊，用戶可以透過對話框輸入「USD」、「美金」、「美」、「JPY」、「日圓」、「日」、「港幣」、「港」等關鍵字，來查詢台灣銀行最新的匯率資訊。<br/>
程式碼的主要流程如下：
- 定義一個 exchange_url 變數，表示台灣銀行匯率網頁的網址。
- 使用 requests 模組指定的 URL 發送 GET 請求，獲取網頁的 HTML 內容，將結果儲存在exchange_rate_res變數中。
- 使用 bs4 模組將網頁內容轉換為 BeautifulSoup 物件，將HTML內容轉換為一個 Soup 物件 exchange_rate_soup，以便於進行數據抓取。
- 定義一個 get_exchange_rate(currency)函數，傳入貨幣參數currency，根據該參數抓取匯率資訊並返回結果。
- 從網頁中解析出牌價最新掛牌時間，並將其儲存在 rate_time_element 變數中。
- 從匯率網頁中抓取牌告匯率表格，並將儲存在 exchange_rate_table 變數中。
- 定義一個 supported_currencies 列表，包含了台灣銀行支援的所有貨幣種類。
- if currency not in supported_currencies：如果傳入的貨幣種類currency不存在列表中，則返回一條找不到匯率信息。
- for tr in exchange_rate_table.find_all('tr')：逐一解析資料表格中的每一列<td>，找到符合輸入幣別的那一列，並抓取該幣別的匯率資訊。
- if currency_td and currency in currency_td.text.strip() 如果當前行<tr>的貨幣種類 HTML 元素存在，且該貨幣符合傳入的參數currency，則從中抓取現金買入匯率、現金賣出匯率、即期買入匯率、即期賣出匯率等匯率資訊。
- message：將匯率資訊組成一個字串，並回傳該字串。
- @handler.add(MessageEvent, message=TextMessage) : <br/>使用 line-bot-sdk 模組中的 handler，偵測 Line Bot 接收到的訊息類型是否為文字訊息，<br/>
從訊息事件中獲取訊息的文字內容，儲存在 msg_text 變數中。<br/>
- 使用條件判斷來確認訊息是否為某個特定的匯率名稱或代碼，如果符合任何一個條件，則呼叫 get_exchange_rate 函式獲取匯率資訊，<br/>
並將回應的訊息傳送回 LINE 平台，讓 linebot 將回應訊息發送給使用者。

### 台灣銀行-每日金價
```python
# 台灣銀行-每日金價
gold_url = 'https://rate.bot.com.tw/gold?Lang=zh-TW'
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
    return message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg_text = event.message.text
	if msg_text == '黃金' or msg_text == '金':
        reply_text = get_gold_price()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='黃金存摺 每 1 公克 (新臺幣元)\n'+ gold_time_element + '\n' + reply_text))
```

這段程式碼主要是用來爬取台灣銀行的每日金價資訊，使用者輸入特定的文字（如「黃金」或「金」）linebot 就會回覆對應的黃金價格。<br/>
程式碼的主要流程如下：
- gold_url : 定義一個URL變數，表示台灣銀行的每日金價網頁。
- gold_res : 使用 requests 模組的 get 方法去取得金價網頁的資料。
- gold_soup : 使用 beautifulsoup4 模組中的 BeautifulSoup 方法，將取得的網頁資料轉換成可解析的物件。
- gold_table : 從解析出來的資料中，找到表格元素(table)並且標題為新臺幣黃金牌價，接著再找到表格的 tbody 元素。
- gold_time_element : 從解析出來的資料中，找到時間元素(div)，並且類別為 pull-left trailer text-info，接著將該元素的文字內容去除前後的空白。
- 定義一個 get_gold_price()函數，用來取得每個商品的名稱和價格。
- for tr in gold_table.find_all('tr'): 使用 for 迴圈遍歷每一個表格行，並取出商品名稱和價格。
- name 和 price : 找到每個列中的名稱(td)元素，並將它的文字內容去除前後的空白。
- message += f'{name}: {price.split()[0]}\n' : 將每個商品名稱和價格，組合成一個字串(message)。

### 美食推薦
```python
def get_delicacy_food(city):
    # 向愛食記網站發送請求，獲取縣市的餐廳資訊，取得最高人氣 
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
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg_text = event.message.text
	# 判斷是否為縣市名稱，如果是，則呼叫 get_delicacy_food 函式取得訊息
    # 使用[endswith] 表示以 "市" 或 "縣"結尾
    elif  msg_text.endswith('市') or msg_text.endswith('縣'):
        reply_text = get_delicacy_food(msg_text)
        line_bot_api.reply_message( event.reply_token,TextSendMessage(text=reply_text))
```

這段程式碼主要是使用者輸入一個縣市名稱時，程式會從「愛食記」網站上搜尋這個縣市的餐廳資訊，並回傳最受歡迎的前五個餐廳的名稱、評價和地址等資訊。<br/>
程式碼的主要流程如下：
- 定義一個函式 get_delicacy_food(city)，該函式需要傳入一個參數 city 表示要查詢的縣市名稱。
- 在函式內部，利用 requests 模組向「愛食記」網站發送 GET 請求，獲取該縣市的美食餐廳資訊，並使用 BeautifulSoup 模組進行網頁內容的解析，取得前五筆餐廳資訊。
- 將取得的餐廳資訊整理成一個字串 message，包括縣市名稱、餐廳名稱、評價和地址等。
- 利用 LINE Bot 的 reply_message() 方法回傳 message 給使用者。
- 定義了一個事件處理函式 handle_message(event)，用於處理收到的使用者訊息。
- 如果使用者輸入的是縣市名稱（以「市」或「縣」結尾），則呼叫 get_delicacy_food() 函式獲取訊息，將取得的餐廳資訊回傳給使用者。

### 每日星座
```python
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
	if  msg_text.endswith('座'):
        # 取得對應星座的今日運勢
        today_text = get_today_star(msg_text)
        # 回覆使用者取得的今日運勢     line_bot_api.reply_message(event.reply_token,TextSendMessage(text=today_text))
```

這段程式主要功能是輸入星座名稱，取得當日的星座運勢，並回覆給使用者。
- 定義一個函式 def get_today_star(star_text)該函式需要傳入一個參數star_text，用來接收使用者輸入的星座名稱。
- 建立一個空字串變數message，用來存放最後的回覆訊息。
- 建立一個字典star_list，將星座名稱作為key，編號作為value。
- if star_text in star_list：判斷使用者輸入的星座名稱是否存在於star_list字典中。
- star_id = star_list[star_text]：取得使用者輸入的星座名稱對應的星座編號。
- star_url：建立一個星座網站的網址，並將star_id帶入網址中。
- 建立一個headers，模擬一個瀏覽器請求，使用requests向網站發送GET請求，獲取網頁回應，再將網頁回應的編碼設置為UTF-8。
- 利用 BeautifulSoup 模組解析原始碼，並取得今日星座運勢的內容 today_content。
- 從 today_content 中取得文字內容 today_text，並刪除開頭和結尾的空格。
- 使用 datetime 模組取得當前日期 today。
- 將 today 和 today_text 組合為訊息文字，存放在 message 變數中。
- handle_message 函式會將使用者傳來的訊息文字存放在變數中，並檢查訊息文字是否以 "座" 結尾。如果是，則呼叫 get_today_star 函式取得對應星座的今日運勢，並將運勢文字回傳給使用者。

### 注意事項: <br/>
因網站有流量限制有時回應會比較慢，爬蟲的網頁如有更動，可能會造成沒有回應。

程式執行畫面 https://youtu.be/bo65i3EyMno



