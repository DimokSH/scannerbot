import requests
import json
import os
import logging
from dotenv import load_dotenv

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем обработчик для записи в файл
file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def askIi(tovarName):
    logger.info(f"Функция askIi запущена для товара: {tovarName}")
    load_dotenv()
    logger.info("Переменные окружения загружены")

    gemini_api_key = os.getenv("newGEMINI_API_KEY")
    myProxyAdressDD = os.getenv("newmyProxyAdressDD")

    if not gemini_api_key or not myProxyAdressDD:
        logger.error("API ключ или прокси не найдены в окружении")
        return 'какая-то ошибка'

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
    headers = {'Content-Type': 'application/json'}
    proxies = {"http": myProxyAdressDD, "https": myProxyAdressDD}

    print(tovarName)
    tt = (f'дай подробные описание характеристик товара {tovarName}. '
          f'Ответ представь в виде json, без древовидной структуры, всё на одном уровне. '
          f'Название свойств пиши на русском языке. '
          f'Используй поиск в интернете. '
          f'Напиши источник откуда взялись данные')

    data = {"contents": [{"parts": [{"text": tt}]}]}
    logger.info(f"Сформирован запрос: {tt[:100]}...")

    try:
        logger.info(f"Отправка запроса к Gemini API через прокси: {myProxyAdressDD}")
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data),
            proxies=proxies
        )
        response.raise_for_status()
        logger.info("Запрос успешно выполнен")

        response_data = response.json()
        result = extract_gemini_text(response_data)
        logger.info("Данные успешно извлечены из ответа")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса: {str(e)}", exc_info=True)
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"HTTP статус: {e.response.status_code}")
            logger.error(f"Ответ сервера: {e.response.text[:500]}")
        return 'какая-то ошибка'
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
        return 'какая-то ошибка'


def extract_gemini_text(gemini_response_data):
    try:
        logger.info("Извлечение текста из ответа Gemini")
        if not gemini_response_data:
            logger.warning("Пустой ответ Gemini")
            return None

        if 'candidates' not in gemini_response_data or not gemini_response_data['candidates']:
            logger.error("Ключ 'candidates' отсутствует или пуст")
            return None

        first_candidate = gemini_response_data['candidates'][0]
        if 'content' not in first_candidate or 'parts' not in first_candidate['content']:
            logger.error("Некорректная структура кандидата")
            return None

        for part in first_candidate['content']['parts']:
            if 'text' in part:
                text_content = part['text'].strip()
                logger.info("Текст ответа получен")

                # Очистка форматирования
                if text_content.startswith('```json'):
                    text_content = text_content[6:].strip()
                if text_content.endswith('```'):
                    text_content = text_content[:-3].strip()

                logger.info("Форматирование очищено")
                return text_content

        logger.warning("Текстовые части не найдены")
        return None
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Ошибка обработки: {str(e)}", exc_info=True)
        return None