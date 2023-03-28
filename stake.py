import requests
import json
import time
import sys
import os

# Fungsi untuk memecahkan captcha menggunakan 2captcha API
def solve_captcha(image_url, api_key):
    captcha_params = {
        'method': 'post',
        'json': 1,
        'key': api_key,
        'file': image_url
    }
    captcha_response = requests.post('https://2captcha.com/in.php', data=captcha_params)
    captcha_id = captcha_response.json()['request']
    captcha_params = {
        'method': 'get',
        'json': 1,
        'key': api_key,
        'action': 'get',
        'id': captcha_id
    }
    while True:
        captcha_response = requests.get('https://2captcha.com/res.php', params=captcha_params)
        captcha_json = captcha_response.json()
        if captcha_json['status'] == 0:
            time.sleep(5)
        else:
            return captcha_json['request']

# Fungsi untuk mengirim permintaan HTTP ke endpoint "/settings/offers" pada situs stake.ac dan mengekstrak informasi bonus drop yang tersedia
def get_offers(api_key):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url = 'https://stake.ac/settings/offers'
    response = requests.get(url, headers=headers)
    response_text = response.text
    if "Please enter the correct code from the image." in response_text:
        captcha_url = "https://stake.ac/captcha?"+ str(int(time.time()*1000))
        captcha_text = solve_captcha(captcha_url, api_key)
        print(f"Solving captcha: {captcha_text}")
        response = requests.post(url, headers=headers, data={'captcha': captcha_text})
        response_text = response.text
    offers = json.loads(response_text)
    return offers

# Fungsi untuk mengirim permintaan HTTP ke endpoint "/settings/offers/redeem" pada situs stake.ac dengan kode bonus drop dan jenis mata uang (misalnya: "trx") yang dimasukkan dari terminal
def redeem_bonus(api_key, bonus_code, currency):
    # set headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://stake.ac/settings/offers'
    }

    # set data to post
    data = {
        'bonusCode': bonus_code,
        'currency': currency,
        'apiKey': api_key
    }

    # post the request to redeem the bonus
    response = requests.post('https://stake.ac/ajax/redeem-bonus', headers=headers, data=data)

    # check if the request is successful
    if response.status_code == 200:
        # parse the response JSON data
        response_data = json.loads(response.text)

        # check if the bonus is successfully redeemed
        if response_data['success'] == True:
            print(f"Bonus redeemed successfully. Bonus amount: {response_data['amount']}.")
        else:
            print(f"Failed to redeem bonus. Reason: {response_data['message']}.")
    else:
        print(f"Failed to redeem bonus. HTTP status code: {response.status_code}.")
