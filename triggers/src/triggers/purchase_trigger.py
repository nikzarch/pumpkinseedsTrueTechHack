import requests
from util.generic_api_usage import get_data,update,delete_records,create_fields

def parse_quantity(quantity_str):
    if isinstance(quantity_str, str):
        return [int(q.strip()) for q in quantity_str.split(',') if q.strip().isdigit()]
    elif isinstance(quantity_str, int):
        return [quantity_str]
    return []

def archive(archive_url, api_key, records):
    try:
        for record in records:
            fields = record['fields']
            fields.pop('ID закупки', None)
            fields.pop('Почта ответсвенного лица', None)
            if not create_fields(archive_url, api_key, fields):
                raise requests.exceptions.RequestException
        return [r['recordId'] for r in records]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при архивации записей: {e}")
        return []

def process_records(data, api_key, archive_url, purchase_url, delivery_url, finance_url):
    on_the_way = []
    cancelled = []
    finance_data = get_data(finance_url, api_key)['data']['records']
    if not all([data, finance_data]):
        return False
    in_finance = set()
    for record in finance_data:
        in_finance.add(record['fields']['Причина расходов'].split('№')[-1])
    
    for record in data['data']['records']:
        total = 0
        try:
            total = record['fields']['Общая стоимость']
        except KeyError:
            try:
                s = parse_quantity(record['fields']['Стоимость товаров'])
                k = parse_quantity(record['fields']['Количество'])
                if len(s) == len(k):
                    for i in range(len(s)):
                        total += int(s[i])*int(k[i])
                update(purchase_url, api_key, record['recordId'], {'Общая стоимость': total})
            except KeyError as e:
                pass
        try:
            status = record['fields']['Статус закупки']
        except KeyError as e:
            continue
        
        if status == "В пути":
            on_the_way.append(record)
        elif status == "Отменён":
            cancelled.append(record)
        elif status == "Создан":
            if record['fields']['Номер договора'] not in in_finance and total != 0:
                create_fields(finance_url, api_key, {"Статус": "Не обработан", "Причина расходов": f"Затраты по договору №{record['fields']['Номер договора']}","Затраты": total})
            

    for record in on_the_way:
        fields =  record['fields']
        fields.pop('Почта ответсвенного лица', None)
        fields.pop('ID закупки', None)
        create_fields(delivery_url, api_key, fields)
    
    ids = archive(archive_url, api_key, cancelled)
    
    unique_ids_to_delete = list(set(ids+list(map(lambda x: x['recordId'],on_the_way))))
    
    if unique_ids_to_delete:
        delete_success = delete_records(purchase_url, api_key, unique_ids_to_delete)
        if delete_success:
            print(f"Удалено записей из исходной таблицы: {len(unique_ids_to_delete)}")
    
    return {
        'total': len(data['data']['records']),
        'on_the_way': len(on_the_way),
        'cancelled': len(cancelled),
    }

def purchase_request(purchase_url, api_key, archive_url, delivery_url, finance_url):
    try:
        data = get_data(purchase_url, api_key)
            
        stats = process_records(data, api_key, archive_url, purchase_url, delivery_url, finance_url)
        
        print("\n" + "="*50)
        print("Триггер закупок")
        print(f"Всего записей: {stats['total']}")
        print(f"В пути: {stats['on_the_way']}")
        print(f"Отменено: {stats['cancelled']} записей")
        print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")