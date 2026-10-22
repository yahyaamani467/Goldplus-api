from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app) # این خط به مرورگر اجازه می‌دهد به سرور ما وصل شود

@app.route('/')
def home():
    return "GoldPlus API is running!"

@app.route('/api/prices')
def get_prices():
    result = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        # دریافت قیمت دلار، طلا و انس از TGJU
        url = "https://www.tgju.org/"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # پیدا کردن قیمت دلار
        dollar_tag = soup.find('li', {'data-market-row': 'price_dollar_rl'})
        if dollar_tag:
            result['dollar'] = int(dollar_tag.find('span', class_='info-price').text.replace(',', '')) // 10

        # پیدا کردن قیمت طلای ۱۸ عیار
        gold_tag = soup.find('li', {'data-market-row': 'geram18'})
        if gold_tag:
            result['gold18'] = int(gold_tag.find('span', class_='info-price').text.replace(',', '')) // 10

        # پیدا کردن انس جهانی
        ounce_tag = soup.find('li', {'data-market-row': 'ons'})
        if ounce_tag:
            result['ounce'] = float(ounce_tag.find('span', class_='info-price').text.replace(',', ''))

        # محاسبه حباب طلا
        if 'gold18' in result and 'ounce' in result and 'dollar' in result:
            intrinsic = (result['ounce'] * result['dollar']) / 31.1035 * (18 / 24)
            bubble = ((result['gold18'] / intrinsic) - 1) * 100
            result['bubble'] = round(bubble, 2)

        # نفت برنت
        oil_tag = soup.find('li', {'data-market-row': 'oil_brent'})
        if oil_tag:
            result['brent'] = float(oil_tag.find('span', class_='info-price').text.replace(',', ''))

        return jsonify({"status": "success", "data": result})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
