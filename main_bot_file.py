  # очень много импортов

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


import requests
from pprint import pprint
session = requests.session()

  # здесь читаю файлы
  # а) со списком фамилий русских писателей для модерации
with open('greats_list.txt', encoding='UTF-8') as infile:
    greats_list = infile.read().split(',')

  # б) датафрейм с фамилиями и текстами
df =  pd.read_csv('base.csv', encoding='utf=8')
authors = df['name'].tolist()
poem = df['text'].tolist()


  # функция, рисующая облако
def clouds_func(message):
    bot.send_message(message.chat.id, text = 'Cекундочку, листаем странички! 📖')
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
    bot.send_message(message.chat.id, text = 'Готово! Теперь можешь ввести другую фамилию или добавить новый текст через главное меню 🌸')


  # читаем токен из файла (кажется, так надежнее)
with open('token.txt', encoding='UTF-8') as infile:
    token = infile.read()


  # далее - код самого бота

import random
import telebot
from telebot import types

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
  # первое сообщение, которое пишет бот, и клавиатура к нему
def restart(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Чьи книжки есть? 💭'), types.KeyboardButton('Хочу добавить книжку! 💭'))
    hi_text = 'Добро пожаловать в облачное книгохранилище! Ты можешь посмотреть на облако слов для книжек из хранилища или добавить свою книжку 💐\
                \n\n📕 Выбери режим:\n\n'
    bot.send_message(message.chat.id, hi_text, reply_markup=markup, parse_mode="Markdown")


  # потом идут функции, с которыми работает бот

  # функция, которая показывает, чьи книжки есть в базе
def whois_mode(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('В главное меню 💌'))
    ans_text = '✨Сейчас у нас есть такие авторы:\n\n'
    authors = sorted(df['name'].tolist())
    for i in range(len(authors)):
        ans_text = ans_text + authors[i] + '\n'
    ans_text = ans_text + '\n' + 'Хочешь посмотреть на облакo слов? Тогда введи фамилию автора! ✨'
    bot.send_message(message.chat.id, text=ans_text, reply_markup=markup)


  # функция, которая сопровождает добавление документа пользователем
def adding_mode(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('В главное меню 💌'))
    ans_text = 'Ура! \nЗагрузи файл с книгой (в формате txt, в кодировке utf-8)🌹'
    bot.send_message(message.chat.id, text=ans_text, reply_markup=markup)


  # функция для "поломки" 
  # если пользователь внимательно читает условие, она вылезает только после ввода фамилии, которой нет в списке русских писателей 
  # а если пользователь читает не внимательно, я в этой версии считаю, что это вина пользователя
def not_in_lib_mode(message):
    no_text = 'О нет, что-то не то! В книгохранилище не знают такого автора 💔\
        \nМы не можем добавить книгу в базу. Но если хочешь, нарисуем облако слов для загруженного файла.'
    bot.send_message(message.chat.id, no_text, reply_markup=markup2)



  # функция, принимающая документ с книгой и записывающая его текст в переменную
@bot.message_handler(content_types=['document'])
def handle_file(message):
    global new_text
    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('file.txt', 'wb') as new_file:
        new_file.write(downloaded_file)
    with open('file.txt', 'r') as file:
        new_text = file.read()
    bot.reply_to(message, 'Ура, успешно! А теперь введи фамилию автора 🌹')



  # реакция бота на действия пользователя
@bot.message_handler(content_types=['text'])
def mode_main(message):
    global authors, poem, new_text
    
    if message.text == 'В главное меню 💌':
        restart(message)        
   
    elif message.text == 'Чьи книжки есть? 💭':
        whois_mode(message)
   
    elif message.text == 'Хочу добавить книжку! 💭':
        adding_mode(message)
    
    elif message.text in authors:
        clouds_func(message)
    
    elif message.text in greats_list and message.text not in authors:
        bot.send_message(message.chat.id, text='Прекрасно, мы как раз искали этого автора! Добавили в базу, сейчас нарисуем облачко 💘')
        
        poem.append(new_text)
        new_name = message.text
        authors.append(new_name)

        df.loc[len(df.index)] = [len(df.index), new_name, ' ', new_text]  
        df.to_csv('base.csv', header=None, mode='a+')

        clouds_func(message)
    
    elif message.text == 'Хочу!💌':
        poem.append(new_text)
        new_name = message.text
        authors.append(new_name)
        clouds_func(message)
        poem.remove(new_text)
        authors.remove(new_name)
   
    else:
        not_in_lib_mode(message)

  # клавиатура после того, когда пользователь вводит фамилию не из базы русских писателей 
markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup2.add(types.KeyboardButton('Хочу!💌'), types.KeyboardButton('В главное меню 💌'))


  # и запуск бота
bot.polling(none_stop=True, interval=0)
