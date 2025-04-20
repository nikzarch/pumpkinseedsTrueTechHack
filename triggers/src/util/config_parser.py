import configparser
from pathlib import Path

def load_config():
    config = configparser.ConfigParser()
    config_file = Path("config.ini")
    
    if not config_file.exists():
        raise FileNotFoundError("Создайте файл config.ini с параметрами api.purchase_url, api.api_key, api.stocks_url, api.archive_url и api.source_url")
    
    config.read(config_file)
    return {
        'purchase_url': config['api']['purchase_url'],
        'api_key': config['api']['api_key'],
        'stocks_url': config['api']['stocks_url'],
        'archive_url': config['api']['archive_url'],
        'delivery_url': config['api']['delivery_url'],
        'product_url': config['api']['product_url'],
        'notification_url': config['api']['notification_url'],
        'warehouses_url': config['api']['warehouses_url']
    }