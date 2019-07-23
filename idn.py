import gspread
import requests
import telebot
from telebot import types
import logging
import pprint
from oauth2client.service_account import ServiceAccountCredentials
import json
pp = pprint.PrettyPrinter()


NAILS = '88d640bc-6e0a-2f8e-7756-ac215fb12516'  #код категории ногтей

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("KeyG.json", scope)
client = gspread.authorize(creds)
sheet = client.open("idn").sheet1 # Open the spreadhseet

import requests

url = "https://api.aihelps.com/v1/services"

querystring = {"fields":"name,duration,category,price_currency,prices"}

headers = {
    'Authorization': "Bearer 46de41d0-7085-4443-9d0b-7b94e9198b6d"
    }

all_services = requests.request("GET", url, headers=headers, params=querystring)
jall_services = json.loads(all_services.text) #все услуги
nogti = list(filter(lambda x: x['category'] == NAILS, jall_services))
nogti_clear = list(map(lambda x: { x['name']: x['prices']['88d640bc-ae28-9810-7756-ac2162d452a2']}, nogti))
pp.pprint(nogti_clear)


bot = telebot.TeleBot("888444353:AAEUFDsBrmHfzN1SccAiBLXhnpDONX373f8")

kbMain = telebot.types.ReplyKeyboardMarkup(True)  #Главное меню
kbMain.row('📋Услуги‍')
kbMain.row('📞Контакты')
kbMain.row('ℹ️️Про нас')

kbLinks = types.InlineKeyboardMarkup()
button_chat1 = types.InlineKeyboardButton(text="💬Начать чат", url="https://t.me/ivdanil")
button_site = types.InlineKeyboardButton(text="🌐Сайт", url="https://t.me/ivdanil")
button_fb = types.InlineKeyboardButton(text="🔗Facebook", url="https://www.facebook.com/idnbeauty/")
kbLinks.row(button_chat1)
kbLinks.row(button_site)
kbLinks.row(button_fb)

kbCallBack = telebot.types.ReplyKeyboardMarkup(True)
button_contact = types.KeyboardButton(text="📲Передзвоніть мені", request_contact=True)
kbCallBack.row(button_contact, "↩️Назад")



kbCategory = telebot.types.InlineKeyboardMarkup(True)
button_nogti = types.InlineKeyboardButton(text="💅Ногтевой сервис", callback_data='CallNails')
button_stomatolog = types.InlineKeyboardButton(text="Стоматолог", callback_data='0')
kbCategory.row(button_nogti, button_stomatolog)



@bot.message_handler(commands=['start'])
def start_message(message):
    usernick = message.chat.first_name
    userinfo = message.chat.id, message.chat.first_name, message.chat.last_name, message.chat.username
    bot.send_message(message.chat.id, usernick + ", 👋Приветсвуем в IDN Beauty Salon\n", reply_markup=kbMain)
    print(userinfo)
    logger = logging.getLogger("WhoStarted")
    logger.setLevel(logging.INFO)
    #create the logging file handler
    fh = logging.FileHandler("who_start.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(userinfo)

@bot.message_handler(content_types=['text', 'contact'])
def main_menu(message):
    if message.text == '📞Контакты':
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id,
                         "⤵️Нажмите на карту, чтоб проложить маршрут:", reply_markup=kbCallBack)
        bot.send_location(message.chat.id, 50.4535751, 30.4635944, disable_notification=True)
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id,
                             "🇺🇦г. Киев\n"
                             "🚇метро «Политехнический институт»\n"
                             "📌переулок Тбилисский 1\n"
                             "🕘Пн-Вс: 09:00 – 21:00\n"
                             "📱0671523482", reply_markup=kbLinks)

    if message.content_type == 'contact':
        usernick = message.chat.first_name
        bot.send_message(message.chat.id, usernick + ", наш администратор свяжется с Вами в ближайшее время")
        bot.send_message(-393579227, "👤" + usernick + " заказал консультацию:")
        bot.forward_message(-393579227, message.chat.id, message.message_id)

    if message.text == '↩️Назад':
        bot.send_message(message.chat.id, "⤵️Выберите действие", reply_markup=kbMain)

    if message.text == '📋Услуги‍':
        bot.send_message(message.chat.id, "⤵️Выберите категорию", reply_markup=kbCategory)

@bot.callback_query_handler(func=lambda call: True)
def services(call):

    if call.data == 'CallNails':

        filtered_all = []  # Фильтруем список из всех часы и уши
        for item in nogti_clear():
            all_ = item['name']
            filtered_all.append(all_)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="\n".join(filtered_all), reply_markup=kbCategory)
    if call.data == '0':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='new0')



bot.polling(True)
