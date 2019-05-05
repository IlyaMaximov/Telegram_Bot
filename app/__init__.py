import telebot

BOT = None
PERSON_INF = dict()
FOOD_TOKEN = 0

def get_food_token(token):
    global FOOD_TOKEN
    FOOD_TOKEN = token


def init_bot(token):
    global BOT
    BOT = telebot.TeleBot(token, threaded=False)

    from app import handlers