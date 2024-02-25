import telebot
from telebot import types  # Importing types module for creating keyboards
import database_internals  # Import your database functions
import datetime

with open('config.txt', 'r') as f:
    config = f.read().splitlines()
    token = config[0]  # Assuming the first line is the Telegram Bot API token

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Add current page')
    itembtn2 = types.KeyboardButton('View statistics')
    itembtn3 = types.KeyboardButton('Add a new book')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.reply_to(message, "Welcome to the Reading Progress Bot!\n"
                          "How can I assist you today?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_info = {"user_id" : message.from_user.id, 
                 "user_name" : message.from_user.username,
                 "chat_id" : message.chat.id}
    
    user_input = message.text.strip()

    conn, cursor = database_internals.db_start()
    database_internals.create_tables(cursor)
    print("Tables created successfully.")
    if not database_internals.user_exists(cursor, user_info["user_name"]):
        database_internals.insert_user_info(cursor, user_info)
    print("user already in db")


    if user_input.lower() == "add current page":
        add_current_page(message)
    elif user_input.lower() == "view statistics":
        view_statistics(message)
    elif user_input.lower() == "add a new book":
        # Ask for the book name
        bot.reply_to(message, "What is the name of the book?")
        bot.register_next_step_handler(message, ask_pages)
    else:
        bot.reply_to(message, "Invalid option. Please choose a valid option.")

    database_internals.db_stop(conn)

def ask_pages(message):
    # Extract book name from the message
    book_name = message.text.strip()

    # Ask for the number of pages
    bot.reply_to(message, "How many pages does the book have?")
    bot.register_next_step_handler(message, add_book, book_name)

def add_book(message, book_name):
    # Extract number of pages from the message
    pages = message.text.strip()

    # Fixate current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Insert book information into the database
    conn, cursor = database_internals.db_start()
    database_internals.insert_book_info(cursor, {
        "bookname": book_name,
        "book_pages_cnt": pages,
        "start_date": current_date
    })
    database_internals.db_stop(conn)

    # Confirmation message
    bot.reply_to(message, "The book has been successfully added to the database!")

# Function to add current page for reading a book
def add_current_page(message):
    bot.reply_to(message, "Please provide the details to add current page for reading a book.")

    # Implement logic to handle user input and interact with the database

# Function to view statistics
def view_statistics(message):
    bot.reply_to(message, "Here are the statistics.")

    # Implement logic to fetch statistics from the database and send them to the user


# Run the bot
if __name__ == "__main__":
    bot.polling()