import requests

def get_data(url, api_key):
    try:
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе остатков: {e}")
        return None

def update(url, api_key, record_id, fields):
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
        
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обновлении остатков: {e}")
        return False

def create_fields(stocks_url, api_key, fields):
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
    
def delete_records(url, api_key, record_ids):
    if not record_ids:
        return True
        
    try:
        headers = {'Authorization': f'Bearer {api_key}'}
        for rid in record_ids:
            url += "&recordIds="+rid
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при удалении записей: {e}")
        return False