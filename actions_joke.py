import random
from typing import Any, List, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

# рассказывает анекдот
class ActionRandomSong(Action):
    def name(self) -> str:
        return "action_random_song"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        songs = [
            "Знаешь почему у людоеда нет друзей? Потому что он сыт по горло.",
            "А знаешь как слепые преодолевают препятствия? Не смотря ни на что.",
            "Как называется место на кладбище, где сидит охранник? Живой уголок.",
            "Как называется обувь отца? Батинки.",
            "Шел как-то Бог по раю, видит, два сада горит. На грушевый вообще всё равно, а яблочный спас.",
            "Почему компьютер замерз? У него было открыто слишком много окон.",
        ]

        if not songs:
            message = "Я ещё не придумал анекдот."
            dispatcher.utter_message(text=message)
            return [SlotSet("last_bot_message", message)]

        song = random.choice(songs)
        message = f"Ну слушай: {song}"
        dispatcher.utter_message(text=message)

        return [SlotSet("last_bot_message", message)]