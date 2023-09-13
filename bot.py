import asyncio
import logging
import os
import time

from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from selenium import webdriver
from selenium.webdriver.common.by import By

from config import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

webdriver_path = config.webdriver_path

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"executable_path={webdriver_path}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")

# ua = UserAgent()
# chrome_options.add_argument(f"user-agent={ua.random}")

driver = webdriver.Chrome(options=chrome_options)
url = config.embassy_url.get_secret_value()


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Проверить слоты",
        callback_data="raise selenium"
    ))
    await message.answer("Привет. Этот бот позволяет проверять слоты для записи в Посольтво РФ В бангкоке", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "raise selenium")
async def cmd_check(callback: types.CallbackQuery):
    await callback.message.answer(("Ожидайте.."))
    await callback.answer("Ну ну, удачи, lol")
    driver.get(url)

    # Find the CAPTCHA image element by XPath
    captcha_img = driver.find_element(By.XPATH, '/html/body/div/div[3]/form/table/tbody/tr/td[2]/div[4]/img')
    captcha_img.screenshot("capcha.png")
    cap = FSInputFile("capcha.png")
    # await callback.answer_photo(cap, caption="капча из посольства")
    await callback.message.answer_photo(cap, caption="капча из посольства")


@dp.message(F.text)
async def cmd_send_code(message: types.Message):
    await message.answer("Спасибо. Обработка...")
    os.remove("capcha.png")
    captcha_data = message.text

    captha_field = driver.find_element(By.ID, "ctl00_MainContent_txtCode")
    captha_field.send_keys(captcha_data)

    button_1 = driver.find_element(By.ID, "ctl00_MainContent_ButtonA")
    button_1.click()
    time.sleep(2)

    button_2 = driver.find_element(By.ID, "ctl00_MainContent_ButtonB")
    button_2.click()
    time.sleep(3)

    driver.save_screenshot("result.png")

    # driver.close()
    result = FSInputFile("result.png")
    await message.answer_photo(result, caption="Вот результат")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
