from util.config_parser import load_config
import time
from triggers.purchase_trigger import purchase_request
from triggers.delivery_trigger import delivery_request
from triggers.stock_trigger import stock_request

def main():
    config = load_config()
    
    print(f"Сервис мониторинга запущен. URL: {config['purchase_url']}")
    print("Для остановки нажмите Ctrl+C\n")
    
    try:
        while True:
            purchase_request(
                config['purchase_url'],
                config['api_key'],
                config['archive_url'],
                config['delivery_url']
            )
            delivery_request(
                config['api_key'],
                config['archive_url'],
                config['delivery_url'],
                config['stocks_url']
            )
            stock_request(
                config['api_key'],
                config['stocks_url'],
                config['product_url'],
                config['notification_url'],
                config['warehouses_url']
            )
            time.sleep(5)

        
    except KeyboardInterrupt:
        print("\nСервис остановлен")

if __name__ == "__main__":
    main()