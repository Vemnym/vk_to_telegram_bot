import random

import psycopg2
import requests
import telebot
import config
import re
import bitlyshortener

# Setup short_maker_url
shortener = bitlyshortener.Shortener(tokens=config.shortcut_token, max_cache_size=256)

# Setup telegram bot
bot = telebot.TeleBot(config.telegram_TOKEN)


@bot.message_handler(commands=['start'])
def telegram_welcome(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>\nНапишите мне то, что вы ищете."
                     .format(message.from_user, bot.get_me()), parse_mode='html')


@bot.message_handler(content_types=['text'])
def send_to_telegram(message):
    """
    Telegram_bot_logic
    """
    correct_posts = take_posts_from_vk(message)  # get posts from vk.com

    try:  # for get random post from 'correct_posts'
        random_number = random.randint(0, len(correct_posts))
    except:
        random_number = 0

    print(random_number)
    print(len(correct_posts))

    try:
        bot_messeage = bot.send_message(message.chat.id, "Генерируем ссылку")
        correct_posts[random_number] = edit_link(correct_posts[random_number])

        bot.send_message(message.chat.id, correct_posts[random_number])

    except:
        bot.send_message(message.chat.id, "Сорян, но ни чего не нашел :(")
    bot.delete_message(message.chat.id, bot_messeage.message_id)


def edit_link(text):
    # create cashback link
    pattern = '(?:http?:\/\/)?(?:[\w\.]+)\.(?:[a-z]{2,6}\.?)(?:\/[\w\.]*)*\/?'
    link_text = re.findall(pattern, text)
    correct_link = []
    for link in link_text:
        temp = requests.get(str(link)).url
        print(str(link))
        temp = "https://gotbest.by/redirect/cpa/o/qlmyq1ued8i0s6zohuljinyq8rr0m5js/?to=" + str(temp)
        print(temp)
        correct_link.append(temp)

    correct_link = shortener.shorten_urls(correct_link)

    i = 0
    while i < len(link_text):
        text = text.replace(link_text[i], correct_link[i])
        i += 1
    print(link_text)
    print(correct_link)
    return text


def take_posts_from_vk(query):
    """
    get posts from vk.com
    """

    massiv_query = query.text.split(" ")

    perc = 0  # % of search
    bot_messeage = bot.send_message(query.chat.id, str(perc) + "% поиск ")

    all_posts = find_all_posts(query.text)

    if not all_posts:
        for one_query in massiv_query:
            if len(one_query) > 3:
                all_posts.extend(find_all_posts(one_query))
            perc += 100 // len(massiv_query)
    if not all_posts:
        for one_query in massiv_query:
            if len(one_query) > 3:
                for domain in config.domains:
                    response = requests.get('https://api.vk.com/method/wall.search',  # spare request
                                            params={
                                                'access_token': config.vk_token,
                                                'v': config.version,
                                                'domain': domain,
                                                'count': 10,
                                                'query': one_query,
                                            })
                    data = response.json()['response']['items']
                    all_posts.extend(data)

            # update % search message
            perc += 100 // len(config.domains) // len(massiv_query)
            bot.edit_message_text(str(perc) + "% поиск ", query.chat.id, bot_messeage.message_id)
        correct_posts = []
        for post in all_posts:  # filter for posts what have url
            if 'http://ali.pub' in post['text'].lower():
                if query.text.lower() in post['text'].lower():
                    correct_posts.append(post['text'])

        if not correct_posts:
            for post in all_posts:
                if 'http://ali.pub' in post['text'].lower():
                    for part in query.text.split(" "):
                        if part.lower() in post['text'].lower():
                            correct_posts.append(post["text"])

        all_posts = correct_posts

    bot.delete_message(query.chat.id, bot_messeage.message_id)  # delete bot % search message

    return all_posts


def find_all_posts(query):
    all_posts = []
    print(query)
    conn = psycopg2.connect(dbname="postgres",
                            user="postgres",
                            password="postgres",
                            host="db")

    cur = conn.cursor()
    cur.execute("SELECT text FROM products WHERE text LIKE '% {} %';".format(query.lower()))
    for item in cur.fetchall():
        all_posts.extend(item)
    if not all_posts:
        cur.execute("SELECT text FROM products WHERE text LIKE '%{} %';".format(query.lower()))
        for item in cur.fetchall():
            all_posts.extend(item)

    conn.commit()
    cur.close()
    conn.close()

    return all_posts


# RUN telegram bot
bot.polling(none_stop=True)
