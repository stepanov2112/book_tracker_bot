import sqlite3
import os

DATABASE_NAME = 'book_tracker_database.db'

def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books_table (
            book_id             INTEGER PRIMARY KEY,
            bookname            TEXT,
            book_pages_cnt      INTEGER,
            start_date          TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_table (
            user_id             INTEGER PRIMARY KEY,
            user_name           TEXT,
            chat_id             INTEGER
        )   
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_reading (
            user_id             INTEGER,
            book_id             INTEGER,
            date                TEXT,
            current_page        INTEGER,
            FOREIGN KEY (user_id) REFERENCES users_table(user_id),
            FOREIGN KEY (book_id) REFERENCES books_table(book_id)
        )   
    ''')


def insert_user_info(cursor, data):
    cursor.execute('''
        INSERT INTO users_table (user_name, chat_id)
        VALUES (?, ?)
    ''', (data["user_name"], data["chat_id"]))


def insert_book_info(cursor, data):
    cursor.execute('''
        INSERT INTO books_table (bookname, book_pages_cnt, start_date)
        VALUES (?, ?, ?)
    ''', (data["bookname"], data["book_pages_cnt"], data["start_date"]))

    cursor.execute('''
        INSERT INTO daily_reading (user_id, book_id, date, current_page)
        SELECT max(user_id), max(book_id), max(date), max(current_page)
        FROM
        (
            SELECT null as user_id, book_id, start_date as date, 0 as current_page 
            FROM books_table where bookname = ?
            UNION ALL
            SELECT user_id, null as book_id, null as date, null as current_page
            FROM users_table where user_name = ?        
        )
    ''', (data["bookname"], data["user_name"]))


def insert_daily_info(cursor, data):
    cursor.execute('''
        INSERT INTO daily_reading ( book_id, date, current_page)
        VALUES (?, ?, ?)
    ''', (data["book_id"], data["date"], data["current_page"]))


def db_start():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    return conn, cursor


def is_tables_created(cursor):
    if not os.path.isfile(DATABASE_NAME):
        create_tables(cursor)

    
def db_stop(conn):
    conn.commit()
    conn.close()


def user_exists(cursor, user_name):
    cursor.execute('''
        SELECT COUNT(*) FROM users_table WHERE user_name = ?
    ''', (user_name,))
    return cursor.fetchone()[0] > 0


def get_books_by_user(cursor, user_name):
    cursor.execute('''
        SELECT bookname FROM books_table WHERE book_id IN (
            SELECT book_id FROM daily_reading WHERE user_id IN (
                SELECT user_id FROM users_table WHERE user_name = ?
            )
        ) ORDER BY start_date DESC LIMIT 5
    ''', (user_name,))
    return [row[0] for row in cursor.fetchall()]


if __name__ == "__main__":
    pass