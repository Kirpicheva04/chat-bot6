import logging
from dotenv import load_dotenv
import random
from typing import Any, List, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from textblob import TextBlob
from translate import Translator
import spacy

logger = logging.getLogger(__name__)
load_dotenv()

# Загрузка модели spaCy
try:
    nlp = spacy.load("ru_core_news_lg")
except OSError:
    nlp = spacy.load("ru_core_news_md")
except OSError:
    print("Error: spaCy model not found.  Please download one using: python -m spacy download ru_core_news_lg")
    nlp = None

# переводчик
def translate_to_english(text):
    translator = Translator(to_lang="en", from_lang="ru")
    try:
        return translator.translate(text).lower()
    except:
        return text

# функция для анализа тональности
def analyze_sentiment(text):
    try:
        for char in text:
            if (65 <= ord(char) <= 90) or (97 <= ord(char) <= 122):
                return 0.0, "error"

        text = translate_to_english(text)
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

        # Определяем тональность
        if polarity > 0.1:
            sentiment = "позитивный"
        elif polarity < -0.1:
            sentiment = "негативный"
        else:
            sentiment = "нейтральный"

        return polarity, sentiment

    except Exception as e:
        print(f"Ошибка анализа тональности: {str(e)}")
        return 0.0, "нейтральный"


# Возвращает ответ в зависимости от тональности
def get_sentiment_response(polarity, sentiment):
    responses = {
        "error": [
            "Пишите, пожалуйста, на русском.",
        ],
        "позитивный": [
            "Я вижу у тебя хорошее настроение! Оценка тональности: {:.2f}",
            "Рад видеть вашу улыбку! Тональность: {:.2f}",
            "Какой настрой! Оценка тональности: {:.2f}"
        ],
        "негативный": [
            "Вижу день не задался( Оценка тональности: {:.2f}",
            "Кажется, тебе грустно. Тональность: {:.2f}",
            "Всё будет хорошо, не переживай. Оценка настроения: {:.2f}"
        ],
        "нейтральный": [
            "Ладно. Оценка тональности: {:.2f}",
            "Нейтральный настрой. Тональность: {:.2f}"
        ]
    }
    return random.choice(responses[sentiment]).format(polarity)


class ActionAnalyzeSentiment(Action):
    def name(self) -> str:
        return "action_analyze_sentiment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        message = tracker.latest_message.get("text")

        # Выполняем анализ тональности
        polarity, sentiment = analyze_sentiment(message)

        # Получаем ответ в зависимости от тональности
        sentiment_response = get_sentiment_response(polarity, sentiment)

        # Отправляем сообщение с анализом тональности
        message = sentiment_response
        dispatcher.utter_message(text=message)

        return [SlotSet("last_bot_message", message)]