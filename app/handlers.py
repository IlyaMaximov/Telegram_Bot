'''
Created on 29 апр. 2019 г.

@author: ilyamaximovv
'''
import telebot
import requests
import time
from app import bot, person_inf, food_token

flag_enough = 2

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 'Привет! Я - бот для еды. Поговори со мной.')


@bot.message_handler(commands=['help'])
def handle_help(message):
    if person_inf.get((message.chat.id, 'name')) is None:
        bot.send_message(message.chat.id, 'Вам необходимо зарегестрироваться (напишите /reg)')
    else:
        bot.send_message(message.chat.id, 'Поздравляем, вы успешно зарегестрированы\n')
    bot.send_message(message.chat.id, 'Вот список доступных вам команд:\n \
                     /get_recipe - позволяет находить рецепты')


@bot.message_handler(commands=['reg'])
def handle_reg(message):
    if person_inf.get((message.chat.id, 'name')) is not None:
        bot.send_message(message.chat.id, 'Вы уже прошли регистрацию')
    else :
        bot.send_message(message.chat.id, "Как у тебя имя?")
        bot.register_next_step_handler(message, get_name)


def get_name(message):
    person_inf[(message.chat.id, 'name')] = message.text
    bot.send_message(message.chat.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    person_inf[(message.chat.id, 'surname')] = message.text
    bot.send_message(message.chat.id, 'Спасибо за регистрацию')


@bot.message_handler(commands=['get_recipe'])
def get_receipe(message):
    if person_inf.get((message.chat.id, 'name')) is None:
        bot.send_message(message.chat.id, 'Вы ещё не прошли регистрацию')
        bot.send_message(message.chat.id, 'Вам необходимо зарегестрироваться (напишите /reg)')
    else:
        bot.send_message(message.chat.id,'Введите интересующие вас ингридиенты через запятую:')
        bot.register_next_step_handler(message, get_ingredients)
    
    
def get_ingredients(message):
    ingredients = message.text
    url = "https://www.food2fork.com/api/search?key={food_token}&q={ingredients}"
    url = url.format(food_token = food_token, ingredients = ingredients)
    text = requests.get(url).json()
    i = 0
    if len(text["recipes"]) == 0:
        bot.send_message(message.chat.id, 'Извините, не удалось найти не одного \
                                          рецепта с данными ингридиентами')
    for item in text["recipes"]:
        i += 1
        bot.send_message(message.chat.id, item['source_url'])
        if i % 5 == 0:
            ask_question(message.chat.id)
            global flag_enough
            flag_enough = 2
            while (flag_enough == 2):
                time.sleep(1)
            if flag_enough:
                bot.send_message(message.chat.id, 'Рады что смогли помочь')
                break;
    if not flag_enough:
        bot.send_message(message.chat.id, 'Рецепты закончились')
    

def ask_question(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(chat_id, text='Добавить ещё рецептов?',  reply_markup=keyboard)
    

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global flag_enough
    if call.data == "yes":
        flag_enough = 0
    elif call.data == "no":
        flag_enough = 1
        
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    bot.send_message(message.chat.id, 'Некорректная команда')
