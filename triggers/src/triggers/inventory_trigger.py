import requests
from util.generic_api_usage import get_data,update,delete_records,create_fields
from itertools import product as pd

def parse_quantity(quantity_str):
    if isinstance(quantity_str, str):
        return [int(q.strip()) for q in quantity_str.split(',') if q.strip().isdigit()]
    elif isinstance(quantity_str, int):
        return [quantity_str]
    return []

def process_records(api_key, stocks_url, inventory_url, shortage_url):
    stocks_data = get_data(stocks_url, api_key)
    inventory_data = get_data(inventory_url, api_key)
    if not all([stocks_data, inventory_data]):
        return False
    
    existing_stocks = dict()
    for stock in stocks_data['data']['records']:
        sku = stock['fields']['SKU'][0] if stock['fields'].get('SKU') else None
        warehouse = stock['fields']['Склад'][0] if stock['fields'].get('Склад') else None
        if sku and warehouse:
            existing_stocks[(warehouse, sku)] = int(stock['fields']['Остаток'])

    for inventory in inventory_data['data']['records']:
        fields = inventory['fields']
        skus = fields.get('SKU', [])
        warehouse = fields.get('Склад', [None])[0]
        s = parse_quantity(fields.get('Количество', '0'))
        old = []
        new = []
        for i in range(len(skus)):
            old.append(existing_stocks.get((warehouse, skus[i]), 0))
            new.append(s[i] - existing_stocks.get((warehouse, skus[i]), 0))
        create_fields(shortage_url, api_key, {"Склад": [warehouse],
                                            "SKU": skus,
                                            "Количество по итогу инвентаризации": ",".join(list(map(str,s))),
                                            "Количество теоретическое на момент инвентаризации": ",".join(list(map(str,old))),
                                            "Разность": ",".join(list(map(str,new))),
                                            "Дата": fields.get('Дата', 0)})    
        delete_records(inventory_url, api_key, [inventory['recordId']])

def inventory_request(api_key, stocks_url, inventory_url, shortage_url):
    try:            
        process_records(api_key, stocks_url, inventory_url, shortage_url)
        
        print("\n" + "="*50)
        print("Триггер инвентаризации")
        print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")