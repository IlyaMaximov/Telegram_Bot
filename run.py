import argparse
import time
import app


def parse_args():
    parser = argparse.ArgumentParser(description="Simple telegram bot",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--bot_token-path", default="./bot_token")
    parser.add_argument("--food_token-path", default = "./food_token")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.bot_token_path, "r") as token_file:
        bot_token = token_file.read()
    with open(args.food_token_path, "r") as token_file:
        food_token = token_file.read()
    app.get_food_token(food_token)
    app.init_bot(bot_token)
    print(bot_token, food_token)
    while True:
        try:
            app.bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(1)


if __name__ == "__main__":
    main()