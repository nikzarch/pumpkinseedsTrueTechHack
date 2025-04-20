import requests
from util.generic_api_usage import get,update,delete_records,create_fields
from itertools import product as pd

def process_records(api_key, stocks_url, product_url, notification_url, warehouses_url):
    stocks_data = get(stocks_url, api_key)
    if not stocks_data:
        return False

    products_data = get(product_url, api_key)
    if not products_data:
        return False
    
    warehouses_data = get(warehouses_url, api_key)
    if not warehouses_data:
        return False

    notifications_data = get(notification_url, api_key)
    if not notifications_data:
        return False

    existing_notifications = set()
    for record in notifications_data['data']['records']:
        sku = record['fields']['SKU'][0] if record['fields']['SKU'] else None
        warehouse = record['fields']['Склад'][0] if record['fields']['Склад'] else None
        if sku and warehouse:
            existing_notifications.add((warehouse, sku))

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

        if (warehouse, sku) in existing_notifications:
            continue

        min_stock = min_stocks.get(sku, 0)
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