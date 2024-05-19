import psycopg2

try:
    # пытаемся подключиться к базе данных
    connection = psycopg2.connect(dbname='gigachat', user='postgres', password='1232', host='localhost', port="5432")
    cursor = connection.cursor()
except Exception as e:
    print(e)

async def upload_data(user_id, file_txt, chat_history, chat_id):
    postgres_insert_query = """ INSERT INTO data (id, chat_history, chat_id, file_txt)
                                           VALUES (%s,%s,%s,%s)"""
    record_to_insert = (user_id, chat_history, chat_id, file_txt)
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()

async def load_data(user_id,chat_id):
    postgres_insert_query = """ SELECT file_txt,chat_history FROM data WHERE id = %s AND chat_id = %s"""
    record_to_insert = (user_id,chat_id)
    cursor.execute(postgres_insert_query, record_to_insert)
    data = cursor.fetchall()
    file_txt = data[0][0]
    chat_history = data[0][1]
    connection.commit()
    return file_txt, chat_history

async def update_data(user_id, chat_history, chat_id):
    postgres_insert_query = """ UPDATE data SET chat_history = %s WHERE id = %s AND chat_id = %s"""
    record_to_insert = (chat_history, user_id, chat_id)
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()
