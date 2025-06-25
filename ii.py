import requests
import json
import os
from dotenv import load_dotenv


def askIi(tovarName):
    # gemini_api_key = os.getenv("GEMINI_API_KEY")
    # myProxyAdressDD = os.getenv("myProxyAdressDD")
    load_dotenv()  # Загрузка .env из текущей директории
    gemini_api_key = os.getenv("newGEMINI_API_KEY")
    myProxyAdressDD = os.getenv("newmyProxyAdressDD")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

    headers = {
        'Content-Type': 'application/json'
    }


    print(tovarName)
    tt = f'дай подробные описание характеристик товара {tovarName}. ' \
         f'Ответ представь в виде json, без древовидной структуры, всё на одном уровне. ' \
         f'Название свойств пиши на русском языке. ' \
         f'Используй поиск в интернете. ' \
         f'Напиши источник откуда взялись данные'

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": tt
                    }
                ]
            }
        ]
    }

    proxies = {
        "http": f"{myProxyAdressDD}",
        "https": f"{myProxyAdressDD}"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), proxies=proxies)
        response.raise_for_status()  # Вызовет исключение для ошибок HTTP (4xx или 5xx)

        response_data = response.json()
        # print(json.dumps(response_data, indent=2, ensure_ascii=False))
        return extract_gemini_text(response_data)

    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Статус-код: {e.response.status_code}")
            print(f"Ответ сервера: {e.response.text}")

        return 'какая-то ошибка'


def extract_gemini_text(gemini_response_data):
    try:
        # Проверка наличия ключей в иерархии
        if not gemini_response_data:
            return None

        if 'candidates' in gemini_response_data and gemini_response_data['candidates']:
            first_candidate = gemini_response_data['candidates'][0]

            if 'content' in first_candidate and 'parts' in first_candidate['content']:
                for part in first_candidate['content']['parts']:
                    if 'text' in part:
                        text_content = part['text'].strip()

                        # Очистка от форматирования кода
                        if text_content.startswith('```json'):
                            text_content = text_content[6:].strip()
                        if text_content.endswith('```'):
                            text_content = text_content[:-3].strip()

                        return text_content
        return None
    except (KeyError, IndexError, TypeError) as e:
        print(f"Ошибка при обработке данных: {e}")
        return None