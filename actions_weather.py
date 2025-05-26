import os
from typing import Any, List, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import logging

logger = logging.getLogger(__name__)

class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        api_key = os.getenv("OPEN_WEATHER_KEY")
        city = next(tracker.get_latest_entity_values("city"), None)

        if not city:
            message = "Укажите город, например: 'Погода в городе Москва'"
            dispatcher.utter_message(text=message)
            return [SlotSet("last_bot_message", message)]

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city},RU&appid={api_key}&units=metric&lang=ru"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                weather_info = (
                    f"Погода в городе {data['name']}:\n"
                    f"- Температура: {data['main']['temp']}°C\n"
                    f"- Описание: {data['weather'][0]['description'].capitalize()}\n"
                )
                dispatcher.utter_message(text=weather_info)
                message = weather_info
            else:
                message = f"Ошибка: город '{city}' не найден. Проверьте правильность ввода."
                dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            message = "Не удалось получить информацию о погоде."
            dispatcher.utter_message(text=message)

        return [SlotSet("last_bot_message", message)]