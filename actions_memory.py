import sqlite3
import json
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

DB_PATH = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            favorite_topic TEXT,
            last_seen TEXT,
            extra TEXT
        )
    """)
    conn.commit()
    conn.close()

class ActionSaveUserMemory(Action):
    def name(self):
        return "action_save_user_memory"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        init_db()
        user_id = tracker.sender_id
        name = tracker.get_slot("name")
        favorite_topic = tracker.get_slot("favorite_topic") # Получаем любимую тему из слота

        print(f"ActionSaveUserMemory: Сохраняем имя: {name}, любимую тему: {favorite_topic}")

        extra_data = {}  # Для будущих расширений

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO user_memory(user_id, name, favorite_topic, last_seen, extra)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                  name=excluded.name,
                  favorite_topic=excluded.favorite_topic,
                  last_seen=excluded.last_seen,
                  extra=excluded.extra;
            """, (
                user_id,
                name,
                favorite_topic,
                datetime.utcnow().isoformat(),
                json.dumps(extra_data)
            ))
            conn.commit()
            dispatcher.utter_message(text="Я запомнил вашу информацию.")
        except Exception as e:
            print(f"Ошибка при сохранении в БД: {e}")
            dispatcher.utter_message(text="Произошла ошибка при сохранении информации.")
        finally:
            conn.close()
        return []

class ActionLoadUserMemory(Action):
    def name(self):
        return "action_load_user_memory"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        init_db()
        user_id = tracker.sender_id
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, favorite_topic, extra FROM user_memory WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            name, favorite_topic, extra_json = row
            print(f"ActionLoadUserMemory: Загружено имя: {name}, любимая тема: {favorite_topic}")
            #message = f"Привет{', ' + name if name else ''}! Тебе нравится {favorite_topic if favorite_topic else 'что-то интересное'}."
            #dispatcher.utter_message(text=message) # приветствие в actions это плохо
            return [
                SlotSet("name", name),
                SlotSet("favorite_topic", favorite_topic) # Устанавливаем слот для любимой темы
            ]
        else:
            dispatcher.utter_message(text="Привет! Рад познакомиться.")
            return []