import requests
from util.generic_api_usage import get_data,update,delete_records,create_fields

def process_records(api_key, income_url, expenses_url, finance_url):
    income_data = get_data(income_url, api_key)
    expenses_data = get_data(expenses_url, api_key)

    if not all([income_data, expenses_data]):
        return False
    
    income = 0
    expenses = 0
    for record in income_data['data']['records']:
        income += record['fields']['Сумма']
    for record in expenses_data['data']['records']:
        expenses += record['fields']['Затраты']
    
    update(finance_url, api_key, 'recCRJP3o9hVZ', {'Доход': income, "Расход": expenses})

def finance_request(api_key, income_url, expenses_url, finance_url):
    try:
        process_records(api_key, income_url, expenses_url, finance_url)
        
        print("\n" + "="*50)
        print("Триггер финансов")
        print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")