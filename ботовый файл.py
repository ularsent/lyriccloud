import pandas as pd

import matplotlib.pyplot as plt
from wordcloud import WordCloud

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import re

import collections
from collections import Counter

from pymystem3 import Mystem


df =  pd.read_csv('C:/Users/ulyas/OneDrive/Рабочий стол/прожект/base.csv', encoding='utf=8')
authors = df['name'].tolist()
path = df['path'].tolist()
poem = df['text'].tolist()

def clouds_func(message):
    bot.send_message(message.chat.id, text = 'Cекундочку!')
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = stopwords.words('russian')

    text = poem[authors.index(message.text)]
    text = re.sub(r'[^\w\s]\n\n','',text)

    word_tokenize(text)
    words = [w.lower() for w in word_tokenize(text) if w.isalpha()]
    words = [w for w in words if w not in stop_words]

    top = dict(Counter(words).most_common(30))
    all_top = list(top.keys())

    stop_words = stop_words + all_top
    words = [w.lower() for w in word_tokenize(text) if w.isalpha()]
    words = [w for w in words if w not in stop_words]

    m = Mystem()
    lemmas = ''.join(m.lemmatize(' '.join(words)))

    wordcloud = WordCloud(width = 400, height = 400,
                          background_color ='white', colormap = 'PiYG').generate(lemmas)

    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud, interpolation='bilinear') 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 

    plt.savefig(f'wordcloud_{message.text}.png')
    bot.send_photo(message.chat.id, photo=open(f'wordcloud_{message.text}.png', 'rb'))
    bot.send_message(message.chat.id, text = 'Готово! Теперь можешь ввести другую фамилию или добавить новый текст через главное меню :)')



with open('C:/Users/ulyas/OneDrive/Рабочий стол/прожект/token.txt', encoding='UTF-8') as infile:
    token = infile.read()

import random
import telebot
from telebot import types

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])

def restart(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Чьи книжки есть?'), types.KeyboardButton('Хочу добавить книжку!'))
    hi_text = 'Добро пожаловать в облачное книгохранилище! тут будет много поэтических сборников(:\n\nВыбери режим:\n\n'
    bot.send_message(message.chat.id, hi_text, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(content_types=['text'])
def mode_main(message):
    if message.text == 'В главное меню':
        restart(message)        
    elif message.text == 'Чьи книжки есть?':
        whois_mode(message)
    elif message.text == 'Хочу добавить книжку!':
        adding_mode(message)
    elif message.text in authors:
        clouds_func(message)
    else:
        not_message = 'again pls'
        bot.send_message(message.chat.id, text=not_message)


def whois_mode(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('В главное меню'))
    ans_text = 'Сейчас у нас есть такие авторы:\n\n'
    authors = df['name'].tolist()
    for i in range(len(authors)):
        ans_text = ans_text + authors[i] + '\n'
    ans_text = ans_text + '\n' + 'Хочешь посмотреть на облакo слов? Тогда введи фамилию автора!'
    bot.send_message(message.chat.id, text=ans_text, reply_markup=markup)

def adding_mode(message):
    pass

bot.polling(none_stop=True, interval=0)