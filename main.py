import asyncio
import aiml
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import BotCommand, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from services.classifier import IntentClassifier
from services.generator import Generator
from services.products import get_random_product, find_product_by_text, PRODUCTS 
from config import config


# Иниаилизация бота
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ML классификатор интентов
classifier = IntentClassifier()
classifier.train()

# Fallback генератор
generator = Generator()

# AIML движок
kernel = aiml.Kernel()
kernel.learn("basic.aiml")

# FSM (выбор товара)
class BuyFSM(StatesGroup):
    choosing_category = State()

# Счётчик сообщений (реклама)
message_counter = 0


# Рекламная логика
def add_advertisement(response: str, intent: str, text: str) -> str:
    global message_counter
    message_counter += 1

    # 1. Сильный сигнал: пользователь хочет купить
    if intent == "buy":
        product = find_product_by_text(text) or get_random_product()
        return response + f"\n\nРекомендую: {product} 🚿"

    # 2. Если явно найден товар в тексте
    product = find_product_by_text(text)
    if product:
        return response + f"\n\nПодходит: {product} 🚿"

    # 3. Периодическая реклама
    if message_counter % 5 == 0:
        return response + f"\n\nПопулярный товар: {get_random_product()} 🚿"

    return response


# /start
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Привет! Я помогу подобрать сантехнику 🚿"
    )

# /help
@dp.message(F.text == "/help")
async def help_command(message: Message):
    await message.answer(
        "Я чат-бот для подбора сантехники 🚿\n\n"
        "Я умею:\n"
        "• отвечать на вопросы\n"
        "• помогать с выбором товаров\n"
        "• предлагать сантехнику\n\n"
        "Попробуй написать:\n"
        "«подбери сантехнику» или «что ты умеешь»"
    )

# /products — список всех товаров
@dp.message(F.text == "/products")
async def products_list(message: Message):
    text = "Каталог товаров:\n\n"

    for i, product in enumerate(PRODUCTS, start=1):
        text += f"{i}. {product}\n"

    await message.answer(text)


# Intent handlers (простые сценарии)
def handle_bye(text: str):
    return "До свидания"


def handle_buy(text: str):
    return "Давайте подберём сантехнику"


def handle_thanks(text: str):
    return "Пожалуйста"


intent_handlers = {
    "bye": handle_bye,
    "buy": handle_buy,
    "thanks": handle_thanks,
}


# FSM: выбор категории
@dp.message(BuyFSM.choosing_category)
async def choose_category(message: Message, state: FSMContext):
    text = message.text.lower()
    product = find_product_by_text(text) or get_random_product()

    await message.answer(f"Рекомендую: {product} 🚿")

    # завершаем FSM
    await state.clear()


# Главный обработчик сообщений
@dp.message()
async def handle_message(message: Message, state: FSMContext):
    
    # Нормализация текста
    text = message.text.lower().strip()
    print(f"[LOG] {text}")

    # ML intent
    intent = classifier.predict(text)

    # Intent: buy → старт FSM
    if intent == "buy":
        await state.set_state(BuyFSM.choosing_category)
        await message.answer(
            "Что вам нужно?\n\n"
            "Например: смеситель, ванна, унитаз"
        )
        return

    # Intent handlers (простые ответы)
    if intent in intent_handlers:
        response = intent_handlers[intent](text)
    else:
        response = None

    # AIML (основной диалог)
    if not response:
        clean_text = text.upper()
        response = kernel.respond(clean_text)

    # Product detection (если AIML не сработал)
    if not response or response == "":
        product = find_product_by_text(text)
        if product:
            response = f"Рекомендую: {product} 🚿"

    # Generator fallback
    if not response:
        response = generator.get_response(text)

    # Final fallback
    if not response:
        response = "Я не совсем понял. Можете уточнить?"

    # Реклама (если есть)
    response = add_advertisement(response, intent, text)

    await message.answer(response)


# Команды бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь и возможности"),
        BotCommand(command="products", description="Список товаров"),
    ]
    await bot.set_my_commands(commands)


# Запуск
async def main():
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())