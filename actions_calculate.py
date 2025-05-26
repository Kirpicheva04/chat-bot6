import re
import logging
from typing import Any, List, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

logger = logging.getLogger(__name__)

class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get("text")
        try:

            expr = re.search(r"(\d+)\s*([+-\/*])\s*(\d+)", message)
            if expr:
                a, op, b = expr.groups()
                a, b = int(a), int(b)

                if op == '+':
                    result = a + b
                elif op == '-':
                    result = a - b
                elif op == '*':
                    result = a * b
                elif op == '/':
                    result = a / b if b != 0 else "∞"

                message = f"Ответ: {result}"
                dispatcher.utter_message(text=message)
            else:
                message = "Некорректный ввод чисел. Как должно быть: 'Посчитай 2+2'"
                dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            message = "Не могу вычислить данное выражение("
            dispatcher.utter_message(text=message)

        return [SlotSet("last_bot_message", message)]