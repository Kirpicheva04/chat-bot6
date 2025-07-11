import sqlite3
import json
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Dict, Text, Any, List
from rasa_sdk.events import SlotSet 

DB_PATH = "user_memory.db"

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

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        init_db()
        user_id = tracker.sender_id
        name = tracker.get_slot("name")
        topic = tracker.get_slot("favorite_topic")
        extra_data = {}
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_memory(user_id, name, favorite_topic, last_seen, extra)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              name=excluded.name,
              favorite_topic=excluded.favorite_topic,
              last_seen=excluded.last_seen,
              extra=excluded.extra;
        """, (user_id, name, topic, datetime.utcnow().isoformat(), json.dumps(extra_data)))
        conn.commit()
        conn.close()
        dispatcher.utter_message(text="Буду знать!")
        return []

class ActionLoadUserMemory(Action):
    def name(self):
        return "action_load_user_memory"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        init_db()
        user_id = tracker.sender_id
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, favorite_topic, extra FROM user_memory WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        events = [] # Список событий, которые мы будем возвращать
        if row:
            name, topic, extra_json = row
            dispatcher.utter_message(text=f"Привет, {', ' + name if name else ''}! Я помню, что ты любишь {topic if topic else ''}.")
            events.append(SlotSet("name", name))
            events.append(SlotSet("favorite_topic", topic))
        else:
            dispatcher.utter_message(text="Привет! Меня зовут Ботик.")
        return events # Возвращаем список событий
