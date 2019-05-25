'''
Created on 29 апр. 2019 г.

@author: ilyamaximovv
'''
import time
import telebot
import requests
from app import BOT, PERSON_INF, FOOD_TOKEN

FLAG_ENOUGH = 2


@BOT.message_handler(commands=['start'])
def handle_start(message):
    BOT.send_message(message.chat.id, 'Привет! Я - бот для еды. Поговори со мной.')


@BOT.message_handler(commands=['help'])
def handle_help(message):
    if PERSON_INF.get((message.chat.id, 'name')) is None:
        BOT.send_message(message.chat.id, 'Вам необходимо зарегестрироваться (напишите /reg)')
    else:
        BOT.send_message(message.chat.id, 'Поздравляем, вы уже успешно зарегестрированы\n')
    BOT.send_message(message.chat.id, 'Вот список доступных вам команд:\n \
                     /get_recipe - позволяет находить рецепты')


@BOT.message_handler(commands=['reg'])
def handle_reg(message):
    if PERSON_INF.get((message.chat.id, 'name')) is not None:
        BOT.send_message(message.chat.id, 'Вы уже прошли регистрацию')
    else:
        BOT.send_message(message.chat.id, "Как у тебя имя?")
        BOT.register_next_step_handler(message, get_name)


def get_name(message):
    PERSON_INF[(message.chat.id, 'name')] = message.text
    BOT.send_message(message.chat.id, 'Какая у тебя фамилия?')
    BOT.register_next_step_handler(message, get_surname)


def get_surname(message):
    PERSON_INF[(message.chat.id, 'surname')] = message.text
    BOT.send_message(message.chat.id, 'Спасибо за регистрацию')


@BOT.message_handler(commands=['get_recipe'])
def get_receipe(message):
    if PERSON_INF.get((message.chat.id, 'name')) is None:
        BOT.send_message(message.chat.id, 'Вы ещё не прошли регистрацию')
        BOT.send_message(message.chat.id, 'Вам необходимо зарегестрироваться (напишите /reg)')
    else:
        BOT.send_message(message.chat.id, 'Введите интересующие вас ингридиенты через запятую:')
        BOT.register_next_step_handler(message, get_ingredients)


def get_ingredients(message):
    ingredients = message.text
    url = "https://www.food2fork.com/api/search?key={FOOD_TOKEN}&q={ingredients}"
    url = url.format(FOOD_TOKEN=FOOD_TOKEN, ingredients=ingredients)
    text = requests.get(url).json()
    dish_index = 0
    if not text["recipes"]:
        answer_pattern = 'Извините, не удалось найти не одного рецепта с данными ингридиентами, {name} {surname}'
        answer = answer_pattern.format(name=PERSON_INF[(message.chat.id, 'name')],
                                       surname=PERSON_INF[(message.chat.id, 'surname')])
        BOT.send_message(message.chat.id, answer)
    for item in text["recipes"]:
        dish_index += 1
        BOT.send_message(message.chat.id, item['source_url'])
        if dish_index % 5 == 0:
            ask_question(message.chat.id)
            global FLAG_ENOUGH
            FLAG_ENOUGH = 2
            while FLAG_ENOUGH == 2:
                time.sleep(1)
            if FLAG_ENOUGH:
                BOT.send_message(message.chat.id, 'Рады что смогли помочь, {} {}'.format(
                    PERSON_INF[(message.chat.id, 'name')], PERSON_INF[(message.chat.id, 'surname')]))
                break
    if not FLAG_ENOUGH:
        BOT.send_message(message.chat.id, 'Просим прощения, рецепты закончились, {} {}'.format(
            PERSON_INF[(message.chat.id, 'name')], PERSON_INF[(message.chat.id, 'surname')]))


def ask_question(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    BOT.send_message(chat_id, text='Добавить ещё рецептов?', reply_markup=keyboard)


@BOT.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global FLAG_ENOUGH
    if call.data == "yes":
        FLAG_ENOUGH = 0
    elif call.data == "no":
        FLAG_ENOUGH = 1


@BOT.message_handler(content_types=['text'])
def handle_text_message(message):
    BOT.send_message(message.chat.id, 'Некорректная команда')
