import requests
import time
from util.generic_api_usage import get,update,delete_records,create_fields

def parse_quantity(quantity_str):
    if isinstance(quantity_str, str):
        return [int(q.strip()) for q in quantity_str.split(',') if q.strip().isdigit()]
    elif isinstance(quantity_str, int):
        return [quantity_str]
    return []

def process_skus_and_quantities(record):
    fields = record['fields']
    skus = fields.get('SKU', [])
    quantities = parse_quantity(fields.get('Количество', ''))
    
    return list(zip(skus, quantities))

def archive(archive_url, api_key, records):
    try:
        for record in records:
            fields = record['fields']
            fields.pop('ID закупки', None)
            fields.pop('Почта ответсвенного лица', None)
            fields.pop('Транспортная компания', None)
            if not create_fields(archive_url, api_key, fields):
                raise requests.exceptions.RequestException
        return [r['recordId'] for r in records]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при архивации записей: {e}")
        return []

def process_records(data, api_key, stocks_data, stocks_url, archive_url, delivery_url):
    delivered = []
    cancelled = []
    
    for record in data['data']['records']:
        try:
            record['fields']['Общая стоимость']
        except KeyError:
            try:
                s = parse_quantity(record['fields']['Стоимость товаров'])
                k = parse_quantity(record['fields']['Количество'])
                total = 0
                if len(s) == len(k):
                    for i in range(len(s)):
                        total += int(s[i])*int(k[i])
                update(delivery_url, api_key, record['recordId'], {'Общая стоимость': total})
            except KeyError as e:
                pass
        try:
            status = record['fields']['Статус закупки']
        except KeyError as e:
            continue
        
        if status == "Доставлен":
            delivered.append(record)
        elif status == "Отменён":
            cancelled.append(record)
    
    stock_cache = {}
    for item in stocks_data.get('data', {}).get('records', []):
        fields = item.get('fields', {})
        warehouse = fields.get('Склад', [None])[0]
        sku = fields.get('SKU', [None])[0]
        if warehouse and sku:
            stock_cache[(warehouse, sku)] = {
                'record_id': item['recordId'],
                'current_stock': fields.get('Остаток', 0)
            }
    
    for record in delivered:
        fields = record['fields']
        warehouse = fields['Склад'][0] if fields['Склад'] else None
        
        if not warehouse:
            continue
        
        for sku, quantity in process_skus_and_quantities(record):
            if not sku:
                continue
            
            if (warehouse, sku) in stock_cache:
                stock_info = stock_cache[(warehouse, sku)]
                new_stock = stock_info['current_stock'] + quantity
                update_fields = {
                    "SKU": [sku],
                    "Склад": [warehouse],
                    "Остаток": new_stock,
                    "Дата подсчёта": int(time.time() * 1000)
                }
                
                if update(stocks_url, api_key, stock_info['record_id'], update_fields):
                    print(f"Обновлён остаток для SKU {sku} на складе {warehouse}: {stock_info['current_stock']} → {new_stock}")
            else:
                create_fields = {
                    "SKU": [sku],
                    "Склад": [warehouse],
                    "Остаток": quantity,
                    "Дата подсчёта": int(time.time() * 1000)
                }
                
                if create_fields(stocks_url, api_key, create_fields):
                    print(f"Создан новый остаток для SKU {sku} на складе {warehouse}: {quantity}")
    
    ids = archive(archive_url, api_key, cancelled+delivered)
    
    unique_ids_to_delete = list(set(ids))
    
    # if unique_ids_to_delete:
    #     delete_success = delete_records(delivery_url, api_key, unique_ids_to_delete)
    #     if delete_success:
    #         print(f"Удалено записей из исходной таблицы: {len(unique_ids_to_delete)}")
    
    return {
        'total': len(data['data']['records']),
        'delivered': len(delivered),
        'cancelled': len(cancelled),
    }

def delivery_request(api_key, archive_url, delivery_url, stocks_url):
    try:
        data = get(delivery_url, api_key)
        
        stocks_data = get(stocks_url, api_key)
        if stocks_data is None:
            return
            
        stats = process_records(data, api_key, stocks_data, stocks_url, archive_url, delivery_url)
        
        print("\n" + "="*50)
        print("Триггер доставок")
        print(f"Всего записей: {stats['total']}")
        print(f"В пути: {stats['delivered']}")
        print(f"Отменено: {stats['cancelled']} записей")
        print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")