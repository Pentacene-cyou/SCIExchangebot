""" sciexchangebot database """
import time
import mysql.connector
from sciexchangebot import logger, config

def db_start():
    """ Init MYSQL """
    try:
        database = mysql.connector.connect(
            host= config['database']['host'],
            user= config['database']['user'],
            password= config['database']['password'],
            database= config['database']['database']
        )
        db_cursor = database.cursor()
        db_cursor.execute('SET NAMES utf8mb4')
        db_cursor.execute("SET CHARACTER SET utf8mb4")
        db_cursor.execute("SET character_set_connection=utf8mb4")
        database.commit()
        return database
    except:
        logger.error("数据库无法连接")
        time.sleep(5)
        db_start()

def log(chat_id: int, msg_id: int, user_id: int, doi: str, b_status: int = 0, document_id: int = 0, bot_msg_id: int = 0) -> bool:
    """ log message with database """
    database = db_start()
    db_cursor = database.cursor()
    try:
        db_cursor.execute(f'INSERT INTO doi_doc (chat_id, msg_id, user_id, doi, b_status, document_id, bot_msg_id) VALUES ({chat_id}, {msg_id}, {user_id}, "{doi}", {b_status}, {document_id}, {bot_msg_id})')
        database.commit()
        return True
    except:
        logger.error("DATABASE INSERT ERROR")
        return False

def select(select_column: str, column: str, value: str|int) -> str|int:
    """ log selected from doi message with database """
    database = db_start()
    db_cursor = database.cursor()
    if isinstance(value, str):
        db_cursor.execute(f'SELECT {select_column} FROM doi_doc where {column} = "{value}"')
    elif isinstance(value, int):
        db_cursor.execute(f'SELECT {select_column} FROM doi_doc where {column} = {value}')
    else:
        return 0
    data = db_cursor.fetchall()
    try:
        return int(data[0][0])
    except:
        return 0

def update(column: str, value: str|int, select_column: str, select_value: str|int) -> bool:
    """ log update with database """
    database = db_start()
    db_cursor = database.cursor()
    if isinstance(value, str):
        db_cursor.execute(f'UPDATE doi_doc SET {column} = {value} where {select_column} = "{select_value}"')
        database.commit()
    elif isinstance(value, int):
        db_cursor.execute(f'UPDATE doi_doc SET {column} = {value} where {select_column} = {select_value}')
        database.commit()
    else:
        return False
    return True

def is_in_blacklist(user_id: int) -> list:
    """ check if is in blacklist with database """
    database = db_start()
    db_cursor = database.cursor()
    db_cursor.execute(f'SELECT reason from blacklist where user_id = {user_id}')
    data = db_cursor.fetchall()
    if len(data) == 0:
        return False
    else:
        return data[0][0]

def add_blacklist(user_id: int, reason: str) -> bool:
    """ add blacklist with database """
    database = db_start()
    db_cursor = database.cursor()
    db_cursor.execute(f'SELECT reason from blacklist where user_id = {user_id}')
    data = db_cursor.fetchall()
    if len(data) == 0:
        db_cursor.execute(f'INSERT INTO blacklist (user_id, reason) VALUES ({user_id}, "{reason}")')
        database.commit()
        return True
    else:
        db_cursor.execute(f'UPDATE blacklist SET reason = "{reason}" WHERE user_id = {user_id}')
        database.commit()
        return True

def all_users() -> list:
    """ select all users with database """
    database = db_start()
    db_cursor = database.cursor()
    db_cursor.execute(f'SELECT user_id from doi_doc')
    data = db_cursor.fetchall()
    logger.debug(data)
    user_list = []
    logger.debug(len(data))
    for i in range(0, len(data)):
        user_list.append(data[i][0])
    user_list = set(user_list)
    logger.debug(user_list)
    return user_list

def get_all_unhelped_msg_id() -> list:
    """ get all unhelped message id with database """
    database = db_start()
    db_cursor = database.cursor()
    db_cursor.execute('SELECT msg_id from doi_doc where b_status = 0 order by msg_id DESC')
    data = db_cursor.fetchall()
    all_unhelped_msg_id_list = []
    for i in range(0, len(data)):
        all_unhelped_msg_id_list.append(data[i][0])
    # all_unhelped_msg_id_list = set(all_unhelped_msg_id_list)
    return all_unhelped_msg_id_list
