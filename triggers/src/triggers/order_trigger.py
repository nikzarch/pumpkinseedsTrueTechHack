import requests
from util.generic_api_usage import get_data,update,delete_records,create_fields
from collections import defaultdict
import random

def process_records(api_key, order_url, order_archive_url, product_url, income_url, stock_url):
    orders = get_data(order_url, api_key)
    products = get_data(product_url, api_key)
    stocks_data = get_data(stock_url, api_key)

    if not all([orders, products, stocks_data]):
        return False
    
    product_prices = dict()
    for product in products['data']['records']:
        product_prices[product['recordId']] = product['fields']['Цена']

    existing_stocks = defaultdict(list)
    for stock in stocks_data['data']['records']:
        sku = stock['fields']['SKU'][0] if stock['fields'].get('SKU') else None
        warehouse = stock['fields']['Склад'][0] if stock['fields'].get('Склад') else None
        if sku and warehouse:
            existing_stocks[sku].append((stock['recordId'],stock['fields']['Остаток']))
    
    fulfilled = []
    for order in orders['data']['records']:
        status = order['fields']['Статус']
        fields = order['fields']
        fields.pop("ID", None)
        fields.pop("Время создания", None)
        if status == 'Обработан':
            fulfilled.append(create_fields(order_archive_url, api_key, fields)['data']['records'][0])
            delete_records(order_url, api_key, [order['recordId']])
        elif status == 'Отменён':
            create_fields(order_archive_url, api_key, fields)
            delete_records(order_url, api_key, [order['recordId']])
        elif status == "Создан":
            choice = random.choice(existing_stocks[fields['SKU (ID товара)'][0]])
            s = fields['Количество']*product_prices[fields['SKU (ID товара)'][0]]
            if s > choice[1]:
                update(order_url, api_key, order['recordId'], {"Статус": "Отменён"})
            else:
                update(stock_url, api_key, choice[0], {"Остаток": int(choice[1]) - int(s)})
                update(order_url, api_key, order['recordId'], {"Статус": "В обработке"})
    
    for record in fulfilled:
        fields = {"Статус": "Не обработан"}
        fields['Источник доходов'] = [record['recordId']]   
        fields['Сумма'] = product_prices[record['fields']['SKU (ID товара)'][0]]*record['fields']['Количество']
        create_fields(income_url, api_key, fields)


def order_request(api_key, order_url, order_archive_url, product_url, income_url, stock_url):
    try:
        process_records(api_key, order_url, order_archive_url, product_url, income_url, stock_url)
        
        print("\n" + "="*50)
        print("Триггер заказов")
        print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")