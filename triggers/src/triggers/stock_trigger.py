import requests
from util.generic_api_usage import get_data,update,delete_records,create_fields
from itertools import product as pd

def process_records(api_key, stocks_url, product_url, notification_url, warehouses_url):
    stocks_data = get_data(stocks_url, api_key)
    warehouses_data = get_data(warehouses_url, api_key)
    products_data = get_data(product_url, api_key)
    notifications_data = get_data(notification_url, api_key)
    if not all([stocks_data, warehouses_data, products_data, notifications_data]):
        return False

    existing_notifications = dict()
    for record in notifications_data['data']['records']:
        sku = record['fields']['SKU'][0] if record['fields']['SKU'] else None
        warehouse = record['fields']['Склад'][0] if record['fields']['Склад'] else None
        if sku and warehouse:
            existing_notifications[(warehouse, sku)] = record['recordId']

    existing_stocks = set()
    for stock in stocks_data['data']['records']:
        sku = stock['fields']['SKU'][0] if stock['fields'].get('SKU') else None
        warehouse = stock['fields']['Склад'][0] if stock['fields'].get('Склад') else None
        if sku and warehouse:
            existing_stocks.add((warehouse, sku))

    min_stocks = {}
    product_skus = set()
    for product in products_data['data']['records']:
        sku = product['recordId']
        min_stock = product['fields'].get('Минимальный остаток', 0)
        min_stocks[sku] = min_stock
        product_skus.add(sku)
    
    all_warehouses = set()
    for warehouse in warehouses_data['data']['records']:
        warehouse_id = warehouse['recordId']
        all_warehouses.add(warehouse_id)

    for stock in stocks_data['data']['records']:
        sku = stock['fields']['SKU'][0] if stock['fields']['SKU'] else None
        warehouse = stock['fields']['Склад'][0] if stock['fields']['Склад'] else None
        current_stock = stock['fields'].get('Остаток', 0)
        
        if not all([sku, warehouse]):
            continue

        min_stock = min_stocks.get(sku, 0)
        if (warehouse, sku) in existing_notifications:
            if current_stock >= min_stock:
                delete_records(notification_url, api_key, [existing_notifications[(warehouse, sku)]])
            continue

        if current_stock < min_stock:
            print(f"Нехватка товара: SKU {sku} на складе {warehouse} ({current_stock}/{min_stock})")
            create_fields(notification_url, api_key, {"SKU": [sku], "Склад": [warehouse], "Описание": "Нехватка товара"})
    
    for warehouse, sku in pd(all_warehouses, product_skus):
        if (warehouse, sku) in existing_stocks:
            continue
            
        if (warehouse, sku) in existing_notifications:
            continue
            
        print(f"Отсутствует товар: SKU {sku} на складе {warehouse}")
        create_fields(notification_url, api_key, {"SKU": [sku], "Склад": [warehouse], "Описание": "Нехватка товара"})

    return True

def stock_request(api_key, stocks_url, product_url, notification_url, warehouses_url):
    try:            
        process_records(api_key, stocks_url, product_url, notification_url, warehouses_url)
        
        print("\n" + "="*50)
        print("Триггер запасов")
        print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")