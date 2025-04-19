import requests
import time
import configparser
from pathlib import Path
from datetime import datetime

def load_config():
    config = configparser.ConfigParser()
    config_file = Path("config.ini")
    
    if not config_file.exists():
        raise FileNotFoundError("Создайте файл config.ini с параметрами api.get_url, api.api_key, api.stocks_url и api.archive_url")
    
    config.read(config_file)
    return {
        'get_url': config['api']['get_url'],
        'api_key': config['api']['api_key'],
        'stocks_url': config['api']['stocks_url'],
        'archive_url': config['api']['archive_url']
    }

def get_all_stocks(stocks_url, api_key):
    try:
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(stocks_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе остатков: {e}")
        return None

def update_stock(stocks_url, api_key, record_id, fields):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "records": [{
                "recordId": record_id,
                "fields": fields
            }],
            "fieldKey": "name"
        }
        
        response = requests.patch(stocks_url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обновлении остатков: {e}")
        return False

def create_stock(stocks_url, api_key, fields):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "records": [{
                "fields": fields
            }],
            "fieldKey": "name"
        }
        
        response = requests.post(stocks_url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании остатка: {e}")
        return False
    
def delete_records(delete_url, api_key, records):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        archive_payload = {
            "records": [],
            "fieldKey": "name"
        }
        for record in records:
            delete_url += "&recordIds="+record["recordId"]
        
        response = requests.delete(delete_url, headers=headers, json=archive_payload)
        response.raise_for_status()
        return len(records)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при архивации записей: {e}")
        return 0

def archive_records(archive_url, api_key, records):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        archive_payload = {
            "records": [],
            "fieldKey": "name"
        }
        
        for record in records:
            fields = record['fields']
            archive_payload["records"].append({
                "fields": {
                    "Статус закупки": fields.get('Статус закупки', []),
                    "SKU": fields.get('SKU', []),
                    "Поставщик": fields.get('Поставщик', []),
                    "Количество": fields.get('Количество', 0),
                    "Склад": fields.get('Склад', []),
                    "Дата доставки": fields.get('Дата доставки', 0),
                    "Ответственный логист": fields.get('Ответственный логист', [])
                }
            })
        
        response = requests.post(archive_url, headers=headers, json=archive_payload)
        response.raise_for_status()
        return len(records)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при архивации записей: {e}")
        return 0

def process_delivered(delivered, stocks_data, stocks_url, api_key, archive_url):
    updated_records = 0
    created_records = 0
    
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
    
    records_to_archive = []
    
    for record in delivered:
        fields = record['fields']
        sku = fields['SKU'][0] if fields['SKU'] else None
        warehouse = fields['Склад'][0] if fields['Склад'] else None
        quantity = fields.get('Количество', 0)
        
        if not all([sku, warehouse, quantity]):
            continue
        
        # Если запись существует - обновляем
        if (warehouse, sku) in stock_cache:
            stock_info = stock_cache[(warehouse, sku)]
            new_stock = stock_info['current_stock'] + quantity
            update_fields = {
                "SKU": [sku],
                "Склад": [warehouse],
                "Остаток": new_stock,
                "Дата подсчёта": int(time.time() * 1000)
            }
            
            if update_stock(stocks_url, api_key, stock_info['record_id'], update_fields):
                print(f"Обновлён остаток для SKU {sku} на складе {warehouse}: {stock_info['current_stock']} → {new_stock}")
                updated_records += 1
                records_to_archive.append(record)
        # Если записи нет - создаем новую
        else:
            create_fields = {
                "SKU": [sku],
                "Склад": [warehouse],
                "Остаток": quantity,
                "Дата подсчёта": int(time.time() * 1000)
            }
            
            if create_stock(stocks_url, api_key, create_fields):
                print(f"Создан новый остаток для SKU {sku} на складе {warehouse}: {quantity}")
                created_records += 1
                records_to_archive.append(record)
    
    # Архивируем все обработанные записи

    return updated_records, created_records

def make_request(get_url, api_key, stocks_url, archive_url):
    try:
        headers = {'Authorization': f'Bearer {api_key}'}
        
        # 1. Получаем данные о закупках
        response = requests.get(get_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 2. Фильтруем записи
        delivered, cancelled = process_records(data)
        
        # 3. Получаем все данные об остатках одним запросом
        stocks_data = get_all_stocks(stocks_url, api_key)
        if stocks_data is None:
            return
            
        # 4. Обрабатываем доставленные записи
        updated_count, created_count = process_delivered(
            delivered, stocks_data, stocks_url, api_key, archive_url
        )

        archive_records(archive_url, api_key, delivered+cancelled)
        delete_records(get_url, api_key, delivered+cancelled)
        
        # 5. Выводим результаты
        print("\n" + "="*50)
        print(f"Всего записей: {data['data']['total']}")
        print(f"Доставлено: {len(delivered)} записей")
        print(f"Отменено: {len(cancelled)} записей")
        print(f"Обновлено остатков: {updated_count}")
        print(f"Создано новых остатков: {created_count}")
        print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")

def process_records(data):
    delivered = []
    cancelled = []
    
    for record in data['data']['records']:
        try:
            status = record['fields']['Статус закупки']
        except KeyError as e:
            continue
        
        if status == "Доставлен":
            delivered.append(record)
        elif status == "Отменён":
            cancelled.append(record)
    
    return delivered, cancelled

def main():
    config = load_config()
    
    print(f"Сервис мониторинга запущен. URL: {config['get_url']}")
    print("Для остановки нажмите Ctrl+C\n")
    
    try:
        while True:
            make_request(
                config['get_url'],
                config['api_key'],
                config['stocks_url'],
                config['archive_url']
            )
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nСервис остановлен")

if __name__ == "__main__":
    main()