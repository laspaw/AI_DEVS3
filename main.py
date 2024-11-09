# standard library
import os
import json
from typing import List, Dict, Union
import re
import ast
import operator as op

# pypi repo
import requests
import openai
from icecream import ic
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


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

    def completion(self, system_prompt, question, model="gpt-4o-mini", temperature=0):
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


# region -= previous tasks =-

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
            answer = self.completion(system_prompt, user_question, model="gpt-4o")
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


class S01E03(AIDEVSCommon):
    '''
    Musisz poprawić plik kalibracyjny dla jednego z robotów przemysłowych. To dość popularny w 2024 roku format JSON.
    Dane testowe zawierają prawdopodobnie błędne obliczenia oraz luki w pytaniach otwartych.
    Popraw proszę ten plik i prześlij nam go już po poprawkach. Tylko uważaj na rozmiar kontekstu modeli LLM,
    z którymi pracujesz — plik się w nie zmieści w tym limicie.
    Plik do pobrania zabezpieczony jest Twoim kluczem API. Podmień “TWOJ-KLUCZ” w adresie na wartość klucza z centrali.
    https://centrala.ag3nts.org/data/TWOJ-KLUCZ/json.txt
    Poprawną odpowiedź wyślij proszę pod poniższy adres, w formie takiej, jak w przypadku Poligonu.
    Nazwa zadanie to JSON.
    https://centrala.ag3nts.org/report

    Co trzeba zrobić w zadaniu?
    1.	Pobierasz plik TXT podany wyżej (tylko podmień TWOJ-KLUCZ) na poprawną wartość
    2.	Ten plik się nie zmienia. Nie musisz go pobierać cyklicznie. Jest statyczny
    3.	Plik zawiera błędy w obliczeniach - musisz je poprawić (ale gdzie one są?)
    4.	Plik w niektórych danych testowych zawiera pole “test” z polami “q” (question/pytanie)
    oraz “a” (answer/odpowiedź).
    To LLM powinien udzielić odpowiedzi.
    5.	Rozmiar dokumentu jest zbyt duży, aby ogarnąć go współczesnymi LLM-ami
    (zmieści się w niektórych oknach kontekstowych wejścia, ale już nie w oknie wyjścia).
    6.	Zadanie na pewno trzeba rozbić na mniejsze części, a wywołanie LLM-a prawdopodobnie będzie wielokrotne
    (ale da się to także zrobić jednym requestem)
    7.	W tym zadaniu trzeba mądrze zdecydować, którą część zadania należy delegować do sztucznej inteligencji,
    a którą warto rozwiązać w klasyczny, programistyczny sposób.
    Decyzja oczywiście należy do Ciebie, ale zrób to proszę rozsądnie.
    '''

    def __init__(self):
        super().__init__()
        self.taskname = "JSON"
        self.answer_endpoint = 'https://centrala.ag3nts.org/report'

    def run(self):
        pseudocode = """
        - load file 'S01E03.json' and parse it
        this file has JSON structure like this:
{
    "apikey": "%PUT-YOUR-API-KEY-HERE%",
    "description": "This is simple calibration data used for testing purposes. Do not use it in production environment!",
    "copyright": "Copyright (C) 2238 by BanAN Technologies Inc.",
    // list of test data of 2 types
    "test-data": [
    // type 1: simple question-answer pair
        {
            "question": "1 + 62",
            "answer": 63
        },
    // type 2: simple question-answer pair plus a test for LLM
        {
            "question": "11 + 86",
            "answer": 97,
            "test": {
                "q": "name of the 2020 USA president",
                "a": "???"
            }
        },
    ...
    ]
}   
        - replace "%PUT-YOUR-API-KEY-HERE%" with self.AIDEVS3_ID
        - for type 1 test data, calculate the answer and replace the answer field with the correct one
        - for type 2 test data, ask LLM for the answer and replace the answer field with the correct one
            (use self.completion method to ask LLM)
        save the corrected JSON as 'corrected_S01E03.json' file
        - send the corrected JSON to the endpoint self.answer_endpoint
        """
        my_prompt = "Complete the code in the region task_execution that will follow pseudocode instructions"

        # region task_execution

        # supported operators for safe evaluation
        operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.USub: op.neg,
        }

        def safe_eval(expr):
            """
            Safely evaluate arithmetic expressions.
            """

            def eval_(node):
                if isinstance(node, ast.Num):  # <number>
                    return node.n
                elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
                    return operators[type(node.op)](eval_(node.left), eval_(node.right))
                elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
                    return operators[type(node.op)](eval_(node.operand))
                else:
                    raise ValueError(f"Unsupported expression: {expr}")

            node = ast.parse(expr, mode='eval').body
            return eval_(node)

        # load file 'S01E03.json' and parse it
        with open('S01E03.json', 'r') as f:
            data = json.load(f)

        # Replace "%PUT-YOUR-API-KEY-HERE%" with self.AIDEVS3_ID
        if data.get("apikey") == "%PUT-YOUR-API-KEY-HERE%":
            data["apikey"] = self.AIDEVS3_ID

        # Iterate over "test-data"
        for item in data.get("test-data", []):
            # Evaluate the "question" field and update "answer"
            question = item.get("question")
            if question:
                try:
                    answer = safe_eval(question)
                    item["answer"] = answer
                except Exception as e:
                    print(f"Error evaluating question '{question}': {e}")

            # If there is a "test" object
            test = item.get("test")
            if test and "q" in test:
                # Use self.completion to get the answer to "test.q" and update "test.a"
                test_question = test["q"]
                system_prompt = "You are a helpful assistant."
                test_answer = self.completion(system_prompt, test_question)
                test["a"] = test_answer

        # Save the corrected JSON as 'corrected_S01E03.json'
        with open('corrected_S01E03.json', 'w') as f:
            json.dump(data, f, indent=4)

        # Set self.answer_data to the corrected JSON data
        self.answer_data = data

        # endregion

        reply = self.send_answer()
        ic(reply)

# endregion


if __name__ == "__main__":
    S01E03().run()
