import telebot

bot = None
person_inf = dict()
food_token = 0

def get_food_token(token):
    global food_token
    food_token = token
    

def init_bot(token):
    global bot
    bot = telebot.TeleBot(token)
#   bot = telebot.TeleBot(token, threaded=False)

    from app import handlers