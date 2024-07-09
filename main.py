import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import io
import pandas as pd

##Асинхронная функция для выполнения запроса к API ЦБ
async def fetch_currency_data(session, date_req=None):
    url = f'http://www.cbr.ru/scripts/XML_daily.asp'
    params = {'date_req': date_req} if date_req else {}

    async with session.get(url, params=params) as response:
        return await response.text()

##Функция для обработки данных и получения данных о курсе валют
def parse_currency_data(xml_data):
    root = ET.fromstring(xml_data)
    currency_data = []

    for valute in root.findall('.//Valute[@ID]'):
        valute_id = valute.get('ID')
        valute_data = {
            'name': valute.find('Name').text,
            'code': valute.find('CharCode').text,
            'value': float(valute.find('Value').text.replace(',', '.')),
        }
        currency_data.append(valute_data)

    return currency_data


def plot_currency_data(currency_data):
    df = pd.DataFrame(currency_data)
    df.set_index('code', inplace=True)

    plt.figure(figsize=(15, 8))
    for code in df.index:
        values = df.loc[code, 'value']
        plt.bar(code, values, label=code, width=0.4)

    plt.xlabel('Код валюты')
    plt.ylabel('Курс')
    plt.title('Курс валюты')
    plt.legend(fontsize='small')
    plt.xticks(fontsize=8)
    plt.tight_layout()

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.savefig('exchange_rate_graph.png', format='png')
    plt.close()
    return img_bytes.getvalue()

##Еще одна асинхронная функция для головной части
async def main():
    async with aiohttp.ClientSession() as session:
        xml_data = await fetch_currency_data(session)

    currency_data = parse_currency_data(xml_data)
    img_bytes = plot_currency_data(currency_data)

if __name__ == "__main__":
    asyncio.run(main())
