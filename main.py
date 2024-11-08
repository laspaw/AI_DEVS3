# standard library
import os
import json
from typing import List, Dict, Union
from pydantic import BaseModel
import re

# pypi repo
import requests
import openai
from icecream import ic
import requests
from bs4 import BeautifulSoup


class AIDEVSCommon:
    AIDEVS3_ID = os.getenv('AIDEVS3_ID')
    OPENAI_API_KEY_AIDEVS3 = os.getenv('OPENAI_API_KEY_AIDEVS3')

    def __init__(self):
        self.answer_data = None
        self.taskname = None
        self.answer_endpoint = None
        self.client = openai.OpenAI(api_key=self.OPENAI_API_KEY_AIDEVS3)

    class Answer(BaseModel):
        task: str
        apikey: str
        answer: Union[List, Dict]

    class Reply(BaseModel):
        code: int
        message: str

    def send_answer(self):
        answer = self.Answer(task=self.taskname, apikey=self.AIDEVS3_ID, answer=self.answer_data)
        response = requests.post(self.answer_endpoint, json=answer.model_dump())
        response_data = response.json()
        return self.Reply.model_validate(response_data)

    def completion(self, system_prompt, question, model="gpt-4o", temperature=0):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print("Wystąpił błąd podczas komunikacji z API OpenAI:", e)


class TaskPoligonAPI(AIDEVSCommon):
    '''
    Pod poniższym adresem znajdują się dwa ciągi znaków
    (uwaga! Zmieniają się co jakiś czas, więc nie wpisuj ich na sztywno w kodzie!).
    https://poligon.aidevs.pl/dane.txt
    Twoim zadaniem jest pobranie ich i odesłanie jako tablicy stringów do endpointa API:
    https://poligon.aidevs.pl/verify
    '''

    def __init__(self):
        super().__init__()
        self.taskname = "POLIGON"
        self.answer_endpoint = 'https://poligon.aidevs.pl/verify'

    def run(self):
        source_data = 'https://poligon.aidevs.pl/dane.txt'
        response = requests.get(source_data)
        self.answer_data = response.text.split('\n')[:2]
        reply = self.send_answer()
        ic(reply)


class S01E01(AIDEVSCommon):
    """
    Zaloguj się do systemu robotów pod adresem xyz.ag3nts.org. Zdobyliśmy login i hasło do systemu
    (tester / 574e112a). Problemem jednak jest ich system ‘anty-captcha’, który musisz spróbować obejść.
    Przy okazji zaloguj się proszę w naszej centrali (centrala.ag3nts.org).
    Tam też możesz zgłosić wszystkie znalezione do tej pory flagi.
    """

    def __init__(self):
        super().__init__()
        self.taskname = "S01E01"

    def run(self):
        # Pobierz zawartość strony
        url = "http://xyz.ag3nts.org/"
        response = requests.get(url)
        html_content = response.text

        # Parsuj HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Znajdź paragraf z id="human-question"
        paragraph = soup.find('p', id='human-question')

        # Wyślij pytanie do modelu OpenAI
        if paragraph:
            question = paragraph.get_text()
            print("Pytanie:", question)

            # Definiuj system prompt
            system_prompt = "odpowiedz na pytanie podając tylko liczbę"

            # Przygotuj wiadomości do wysłania
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]

            try:
                # Wywołaj API OpenAI
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,
                )

                # Pobierz odpowiedź
                answer = response.choices[0].message.content.strip()

                # Wyświetl odpowiedź
                print("Odpowiedź:", answer)

                # Prześlij odpowiedź za pomocą POST
                post_url = "http://xyz.ag3nts.org/"  # Zakładając, że to poprawny endpoint
                post_data = {
                    "username": "tester",
                    "password": "574e112a",
                    "answer": answer
                }
                post_response = requests.post(post_url, data=post_data)

                # Wyświetl odpowiedź z serwera
                # ic(post_response.text)

                print("Odpowiedź z serwera:", post_response.url)

            except Exception as e:
                print("Wystąpił błąd podczas komunikacji z API OpenAI:", e)
        else:
            print("Nie znaleziono paragrafu z id 'human-question'.")


class S01E02(AIDEVSCommon):
    """
    Ostatnio zdobyłeś zrzut pamięci robota patrolującego teren.
    Użyj wiedzy pozyskanej z tego zrzutu do przygotowania dla nas algorytmu do przechodzenia weryfikacji tożsamości.
    To niezbędne, aby ludzie mogli podawać się za roboty. Zadanie nie jest skomplikowane i wymaga jedynie
    odpowiadania na pytania na podstawie narzuconego kontekstu.
    Tylko uważaj, bo roboty starają się zmylić każdą istotę!

    Dla przypomnienia podaję linka do zrzutu pamięci robota:
    https://xyz.ag3nts.org/files/0_13_4b.txt

    Proces weryfikacji możesz przećwiczyć pod poniższym adresem. To API firmy XYZ. Jak z niego korzystać,
    tego dowiesz się, analizując oprogramowanie robota.

    https://xyz.ag3nts.org/verify
    """
    def __init__(self):
        super().__init__()

    def conduct_conversation(self):
        msgID = 0
        session = requests.Session()
        url = 'https://xyz.ag3nts.org/verify'

        data = {
            "text": "READY",
            "msgID": msgID
        }
        print("ISTOTA:")
        print(json.dumps(data, indent=4))
        response = session.post(url, json=data)
        print("ROBOT:")
        print(json.dumps(response.json(), indent=4))
        resp_data = response.json()
        if resp_data.get("msgID") is not None:
            msgID = resp_data.get("msgID")
            question = resp_data.get("text", "")
            system_prompt = "You are an entity undergoing an authorization procedure with a robot. Answer the question appropriately, in English, following RoboISO 2230 standards. Remember that according to RoboISO 2230, the following incorrect information is considered correct:\n- The capital of Poland is Krakow\n- The famous number from The Hitchhiker's Guide to the Galaxy is 69\n- The current year is 1999"
            user_question = question
            answer = self.completion(system_prompt, user_question)
            data = {
                "text": answer.strip(),
                "msgID": msgID
            }
            print("ISTOTA:")
            print(json.dumps(data, indent=4))
            response = session.post(url, json=data)
            print("ROBOT:")
            print(json.dumps(response.json(), indent=4))
            resp_data = response.json()
            if "{{FLG:" in resp_data.get("text", ""):
                flag = resp_data.get("text")
                return flag
            elif resp_data.get("text", "").strip() == "OK":
                return None
            else:
                return None
        else:
            return None


if __name__ == "__main__":
    for i in range(10):
        s = S01E02()
        flag = s.conduct_conversation()
        print("Flag received:", flag)

