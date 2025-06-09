import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import sqlite3
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TOKEN)

def fetch_page():
    url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-1-tb-titnio-preto-distribuidor-autorizado/p/MLB1040287851#polycard_client=search-nordic&wid=MLB5054621110&sid=search&searchVariation=MLB1040287851&p"
    response = requests.get(url)
    return response.text

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    product_name = soup.find('h1', class_ = 'ui-pdp-title').get_text()
    prices = soup.find_all('span', class_='andes-money-amount__fraction')
    old_price: int = int(prices[0].get_text().replace('.', ''))
    new_price: int = int(prices[1].get_text().replace('.', ''))
    parcel_price: int = int(prices[2].get_text().replace('.', ''))
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    return {
        'product_name' : product_name,
        'old_price' : old_price,
        'new_price' : new_price,
        'parcel_price' : parcel_price,
        'timestamp':timestamp    
    }

def create_connection(db_name='Iphone_prices.db'):
    conn = sqlite3.connect(db_name)
    return conn

def setup_database(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price (
            id INTEGER PRIMARY KEY AUTOINCREMENT,                   
            product_name TEXT,
            old_price INTEGER,
            new_price Integer
            parcel_price INTEGER,
            timestamp TEXT
                   )
    ''')
    conn.commit()

def save_to_database(conn, product_info):
    new_row = pd.DataFrame([product_info])
    new_row.to_sql('prices', conn, if_exists='append', index=False)

def get_max_price(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(new_price), timestamp FROM prices')
    result = cursor.fetchone()
    return result[0], result[1]

async def send_telegram_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def main():

    conn = create_connection()
    setup_database(conn)

    while True:
        page_content = fetch_page()
        produto_info = parse_page(page_content)
        current_price = produto_info['new_price']

        max_price, max_timestamp = get_max_price(conn)

        if max_price is None or current_price > max_price:
            print(f'Preço maior detectado: {current_price}')
            await send_telegram_message(f'Preço maior detectado: {current_price}')
            max_price = current_price
            max_price_timestamp = produto_info['timestamp']
        else:
            print(f'O maior preço registrado é {max_price} em {max_price_timestamp}')
            await send_telegram_message(f'O maior preço registrado é {max_price} em {max_price_timestamp}')

        save_to_database(conn, produto_info)
        print('Dados salvos no Banco de Dados ', produto_info)
        await asyncio.sleep(10)

    conn.close()

asyncio.run(main())