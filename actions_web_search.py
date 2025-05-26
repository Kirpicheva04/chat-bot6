import webbrowser
from urllib.parse import quote
from typing import Any, List, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionWebSearch(Action):
    def name(self) -> Text:
        return "action_web_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Получаем последнее сообщение пользователя
        message = tracker.latest_message.get("text")

        result = self._perform_search(message)

        dispatcher.utter_message(text=result)
        return [SlotSet("last_bot_message", result)]

    def _perform_search(self, command: Text) -> Text:
        """Выполняет поиск в интернете через webbrowser"""
        try:
            # Проверяем, начинается ли команда с "поиск " и содержит ли она кавычки
            if command.lower().startswith('поиск "') and command.count('"') >= 2:
                # Извлекаем текст между кавычками
                query = command.split('"')[1]

                # Открываем результаты поиска в браузере
                webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
                message = f"Ищу: {query}"
                return message

            message = "Используйте: поиск \"запрос\""
            return message

        except Exception as e:
            message = f"Не могу найти: {str(e)}"
            return message