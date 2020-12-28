import random
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
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>\nНапишите мне то, что вы ищете.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html')


@bot.message_handler(content_types=['text'])
def send_to_telegram(message):
    """
    Telegram_bot_logic
    """
    posts = take_posts_from_vk(message)  # get posts from vk.com
    correct_posts = []

    for post in posts:  # filter for posts what have url
        if 'http://ali.pub' in post['text'].lower():
            if message.text.lower() in post['text'].lower():
                correct_posts.append(post)

    if not correct_posts:
        for post in posts:
            if 'http://ali.pub' in post['text'].lower():
                for part in message.text.split(" "):
                    if part.lower() in post['text'].lower():
                        correct_posts.append(post)

    try:  # for get random post from 'correct_posts'
        random_number = random.randint(0, len(correct_posts))
    except:
        random_number = 0

    print(random_number)
    print(len(correct_posts))

    try:
        bot_messeage = bot.send_message(message.chat.id, "Генерируем ссылку")
        correct_posts[random_number]['text'] = edit_link(correct_posts[random_number]['text'])

        bot.send_message(message.chat.id, correct_posts[random_number]['text'])

    except:
        bot.send_message(message.chat.id, "Сорян, но ни чего не нашел :(")
    bot.delete_message(message.chat.id, bot_messeage.message_id)


def edit_link(text):
    # create cashback link
    pattern = '(?:http?:\/\/)?(?:[\w\.]+)\.(?:[a-z]{2,6}\.?)(?:\/[\w\.]*)*\/?'
    link_text = re.findall(pattern, text)
    correct_link = []
    for link in link_text:
        temp = requests.get(link).url
        temp = "https://gotbest.by/redirect/cpa/o/qlmyq1ued8i0s6zohuljinyq8rr0m5js/?to=" + str(temp)
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

    all_posts = []

    perc = 0  # % of search
    bot_messeage = bot.send_message(query.chat.id, str(perc) + "% поиск ")

    # domain is list group from vk
    domains = ["zaceny",
               "doehalo",
               "godnoten",
               "aloauto",
               "ali_do_3",
               "ali_stallions",
               "ali_yourcars",
               "s_stylist",
               "asianstyleali",
               "alie_kids",
               "instryment_s_kitay"]

    for one_query in massiv_query:
        for domain in domains:
            response = requests.get('https://api.vk.com/method/wall.search',  # main request
                                    params={
                                        'access_token': config.vk_token,
                                        'v': config.version,
                                        'domain': domain,
                                        'count': 100,
                                        'query': one_query
                                    })
            data = response.json()['response']['items']
            all_posts.extend(data)
            if not data:
                response = requests.get('https://api.vk.com/method/wall.get',  # spare request
                                        params={
                                            'access_token': config.vk_token,
                                            'v': config.version,
                                            'domain': domain,
                                            'count': 100,
                                        })
                data = response.json()['response']['items']
                all_posts.extend(data)

            # update % search message
            perc += 100 // len(domains) // len(massiv_query)
            bot.edit_message_text(str(perc) + "% поиск ", query.chat.id, bot_messeage.message_id)

    bot.delete_message(query.chat.id, bot_messeage.message_id)  # delete bot % search message

    return all_posts


# RUN telegram bot
bot.polling(none_stop=True)
