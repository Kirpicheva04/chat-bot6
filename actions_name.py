# actions.py (или actions_memory.py)
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionRememberName(Action):
    def name(self):
        return "action_remember_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        name = tracker.get_slot("name")
        if name:
            return [SlotSet("name", name)] # Только сохраняем имя в слоте
        else:
            return []

class ActionGreetWithName(Action): # Новое действие
    def name(self):
        return "action_greet_with_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        name = tracker.get_slot("name")
        if name:
            dispatcher.utter_message(text=f"Рад тебя видеть снова, {name}!")
        else:
            dispatcher.utter_message(text="Рад познакомиться!")
        return []