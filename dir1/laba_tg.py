import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, Application, ContextTypes, CommandHandler, MessageHandler, filters
import requests
import random
# Токены для погоды с тг ботом и список ключей для запросов
weather_api_key = "81c7520a216cf22d09fa43049d7386c1" 
bot_token = "6017106752:AAGFQmNPwMAzT2sOmXoI3e7n4xgGbI1KO2s"
city = {'Санкт-Петербурге':'Saint%20Petersburg', 
        'Москве':'Moscow', 
        'Лондоне. Лондоне? Да, в Лондоне! Ну… это там, где рыба, чипсы, чай, паршивая еда, отвратная погода, Мэри-ебать-её-в-сраку-Поппинс — Лондон!':'London',
        'Чикаго':'Chicago',
        'Париже':'Paris',
        'SwEeEeEeT HoMe AlAbAmA':'Alabama'
        }
remaining_city = city.copy()
paid_button = '"Платная" погода'    #Надпись на первой кнопке
unpaid_button = 'Бесплатный мемас'  #Надпись на второй кнопке
files_list = []
for i in range(36):
    files_list.append(f"tg{i}.jpg")

remaining_list = files_list.copy()

def get_meme(number = None, v = None):
    global remaining_list
    global files_list
    if not number == None: 
        if v: print(f"tg{number}.jpg\n")
        return f"tg{number}.jpg"
    if len(remaining_list) == 1: 
        if v: print(f"{remaining_list}\n")
        elem = remaining_list[0]
        remaining_list = files_list.copy()
        return elem
    i = random.randrange(0, len(remaining_list)-1)
    if v: print(f"{remaining_list}\n")
    return remaining_list.pop(i)
    

def get_weather(v = None): #метод выплевывает строку с погодой в рандомном городе
    global remaining_city
    global city
    if len(remaining_city) == 0: remaining_city = city.copy()
    requested_city_key = random.choice(list(remaining_city.keys()))   #выбираем рандомный город
    requested_city_index = remaining_city[requested_city_key]           #записываем значение ключа для города
    remaining_city.pop(requested_city_key)  
    if v: print(f"{remaining_city}\n")                                       
    # создаем ссылку для запроса
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={requested_city_index}&appid={weather_api_key}"

    response = requests.get(weather_url)                #записываем полученый json с погодой

    temp_celsius = round(float(response.json()["main"]["temp"])-273.15)     #Вытаскиваем из json строки температуру и переводим из Кельвин в Цельсий
    weather_condition = response.json()["weather"][0]["description"]        #Описание погоды
    wind_velocity = round((float(response.json()["wind"]["speed"])),1)      #скорость ветра
    humidity = int(response.json()["main"]["humidity"])                     #Влажность

    # Формируем строку для вывода
    output = f"Погода в {requested_city_key}:\n\
            Температура:  {temp_celsius}С\n\
            Состояние:  {weather_condition}\n\
            Скорость ветра:  {wind_velocity} м/с\n\
            Влажность:  {humidity}%"
    return output


#Метод start вызывается при получении /start
#Удаляет старую клавиатуру, выводит приветствие и новую клаву
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 

    remove_keyboard = ReplyKeyboardRemove()                                         #удаляет клаву и выводит первую часть приветсвия
    await update.message.reply_text("Welcome!...",reply_markup=remove_keyboard)     #удаляет клаву и выводит первую часть приветсвия

    keyboard = [(KeyboardButton(paid_button), KeyboardButton(unpaid_button))]   #Определяем клавиатуру и надписи на ее кнопках
    markup = ReplyKeyboardMarkup(keyboard)                                      #Объект с размеченой клавой и нашими кнопками
    await update.message.reply_text("...to the cum zone",reply_markup=markup)   #Выводит новую клаву и вторую чатсть приветсвия


#Выводит погоду для случайного города
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    string = get_weather()             #Вызывает написанный ранее метод для погоды и записывает ее в string
    await context.bot.send_message(chat_id=update.effective_chat.id, text=string) #Выводит сообщение со строкой погоды


#Выводит мемасы
async def unpaid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(chat_id=update._effective_chat.id, photo=open(get_meme(),'rb'))


application = ApplicationBuilder().token(bot_token).build() #Объект приложения которое будет работать в боте

# Далее определяется хендлеры для вызова команд по получченому тексту
start_handler = CommandHandler('start', start) #Когда получаем /start вызываем мето start
application.add_handler(start_handler)         #Добавляем хендлер в приложение

paid_handler = MessageHandler(filters.Text(paid_button), paid) #Получаем текст с 1 кнопки вызываем paid
application.add_handler(paid_handler)

unpaid_handler = MessageHandler(filters.Text(unpaid_button), unpaid) #Получаем текст с 2 кнопки вызываем unpaid
application.add_handler(unpaid_handler)

application.run_polling() #Запускаем постоянную проверку новых сообщений в боте
