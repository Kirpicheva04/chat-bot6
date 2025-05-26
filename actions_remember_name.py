from typing import Any, List, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import spacy # Перемещено в actions_analyze_sentiment
import logging # Перемещено в actions_analyze_sentiment

logger = logging.getLogger(__name__) # Перемещено в actions_analyze_sentiment

#Не нужен импорт load_dotenv()

class ActionRememberName(Action):
    def name(self) -> Text:
        return "action_remember_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        lang = domain.get("config", {}).get("language", "ru")
        text = tracker.latest_message.get("text")

        from actions.actions_analyze_sentiment import nlp
        if nlp is None:
            message = "К сожалению, я не могу сейчас запомнить ваше имя.  Пожалуйста, попробуйте позже."
            dispatcher.utter_message(text=message)
            return [SlotSet("last_bot_message", message)]

        doc = nlp(text)
        name = next((ent.text for ent in doc.ents if ent.label_ == "PER"), None)

        if not name:
            dispatcher.utter_message(response_key="utter_ask_name") # ИСПРАВЛЕНО
            return []

        message = f"Приятно познакомиться, {name}!" if lang == "ru" else f"Nice to meet you, {name}!"
        dispatcher.utter_message(text=message)
        return [SlotSet("name", name), SlotSet("last_bot_message", message)]