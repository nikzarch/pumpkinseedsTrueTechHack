from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import os
import logging

from APIService import APIClient
from PDFService import create_delivery_document

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

api_client = APIClient(timeout=15)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! \n/get_contract - получение документа по запупкам"
                                    "\n/it_appeal - получение формы обращения к it отделу")


async def get_contract(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response_base = api_client.get(
            base_url="https://true.tabs.sale/fusion/v1/datasheets/dstEpz6wPXEZmBzz2R/records?viewId=viwTzNnTm4q4n&fieldKey=name",
            headers={"Authorization": f"Bearer {os.getenv('API_TOKEN')}"}
        )

        response_provider = api_client.get(
            base_url="https://true.tabs.sale/fusion/v1/datasheets/dstSsUFMntVXHRGlUc/records?viewId=viwsLEXf8CSKp&fieldKey=name",
            headers={"Authorization": f"Bearer {os.getenv('API_TOKEN')}"}
        )

        response_product = api_client.get(
            base_url="https://true.tabs.sale/fusion/v1/datasheets/dstR95kW46WwtnVxnw/records?viewId=viwj37ePoX8uk&fieldKey=name",
            headers={"Authorization": f"Bearer {os.getenv('API_TOKEN')}"}
        )

        providers = {p['recordId']: p for p in response_provider['data']['records']}
        products = {p['recordId']: p for p in response_product['data']['records']}
        bases = {}
        bases_providers = []

        for base in response_base['data']['records']:
            bases[base['recordId']] = base
            bases_providers.extend(base.get('fields', {}).get('Поставщик', []))

        keyboard = []
        for provider in providers.values():
            if provider['recordId'] not in bases_providers:
                continue

            company = provider.get('fields', {}).get('Компания', 'Без названия')
            keyboard.append([InlineKeyboardButton(
                text=company,
                callback_data=f"supplier_{provider['recordId']}"
            )])

        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "📋 Выберите поставщика из списка:",
                reply_markup=reply_markup
            )
            context.user_data.update({
                'providers': providers,
                'products': products,
                'bases': bases
            })
        else:
            await update.message.reply_text("❌ Нет доступных поставщиков для выбора.")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка при генерации документа.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("supplier_"):
        # Обработка выбора поставщика
        provider_id = query.data.split("_")[1]
        context.user_data['selected_provider_id'] = provider_id

        contract_keyboard = []

        for base in context.user_data.get('bases').values():
            contract_keyboard.append(
                [InlineKeyboardButton(base['fields']['Номер договора'],
                                      callback_data="contract_" + base['fields']['Номер договора'])]
            )

        reply_markup = InlineKeyboardMarkup(contract_keyboard)

        await query.edit_message_text(
            "📋 Выберите номер договора:",
            reply_markup=reply_markup
        )

    elif query.data.startswith("contract_"):
        contract_number = query.data.split("_")[1]
        provider_id = context.user_data.get('selected_provider_id')

        if not provider_id:
            await query.edit_message_text("⚠️ Ошибка: поставщик не выбран")
            return

        data = context.user_data
        selected_provider = data['providers'].get(provider_id)

        if not selected_provider:
            await query.edit_message_text("⚠️ Поставщик не найден")
            return

        try:
            company = selected_provider.get('fields', {}).get('Компания', 'Без названия')
            phone = selected_provider.get('fields', {}).get('Номер телефона', 'Не указан')
            email = selected_provider.get('fields', {}).get('Почта', 'Не указана')

            value = 0
            goods_list = []
            for base in data['bases'].values():
                d = base['fields']['Общая стоимость']
                if (provider_id in base.get('fields', {}).get('Поставщик', [])
                        and base['fields']['Номер договора'] == contract_number):
                    skus = base.get('fields', {}).get('SKU', [])
                    for i in range(len(skus)):
                        product = data['products'].get(skus[i])
                        if product:
                            goods_list.append({
                                'name': product.get('fields', {}).get('Название товара', 'Без названия'),
                                'quantity': base['fields']['Количество'].split(',')[i],
                                'price': product.get('fields', {}).get('Цена', 0)
                            })
                            value = d

            goods_for_pdf = [{
                "name": item['name'],
                "quantity": item['quantity'],
                "price": item['price']
            } for item in goods_list] if goods_list else [{"name": "Товары не найдены", "quantity": 0, "price": 0}]

            await query.edit_message_text(
                f"✅ Выбран поставщик: {company}\n"
                f"📄 Номер договора: {contract_number}\n"
                f"☎ Телефон: {phone}\n"
                f"📧 Почта: {email}\n"
                f"📦 Найдено товаров: {len(goods_list)}\n\n"
                "🔄 Формирую документ..."
            )

            create_delivery_document(
                value=value,
                doc_number=contract_number,
                doc_date="______",
                supplier={
                    "name": company,
                    "phone": phone,
                    "email": email
                },
                buyer={
                    "name": "ООО «Дикая Черешня»",
                    "phone": "+7 (999) 990-99-99",
                    "email": "office@cherry.ru"
                },
                delivery_date="______",
                goods=goods_for_pdf
            )

            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=open("delivery_document.pdf", "rb"),
                caption=f"📄 Договор №{contract_number} готов"
            )

        except Exception as e:
            logger.error(f"Ошибка: {e}", exc_info=True)
            await query.edit_message_text("❌ Ошибка при создании документа")


async def it_appeal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Форма для общания в it отдел:\nhttps://true.tabs.sale/share/shr5STp9HtQnoeKpYRUaQ")


def main():
    if not TOKEN:
        logger.error("Токен не найден в .env файле!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("get_contract", get_contract))
    app.add_handler(CommandHandler("it_appeal", it_appeal))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(supplier|contract)_"))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()