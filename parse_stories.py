import requests
from bs4 import BeautifulSoup
import os

URL = "https://thetruestory.news/ru/russia"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def parse_stories():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    stories = soup.find_all("a", class_="s2 story illustrated")

    results = []

    for story in stories[:7]:  # Возьмём 7 новостей, как в шаблоне
        # Заголовок
        headline = story.select_one(".s2.message.headline.pinned h2")
        title = headline.get_text(strip=True) if headline else "Без заголовка"

        # Первый источник (название + ссылка)
        first_message_source = story.select_one(".s2.message.headline.pinned .s2.source")
        source_name = first_message_source.get_text(strip=True) if first_message_source else ""

        # Попытка взять ссылку на оригинал из меню источников (первый источник в списке)
        source_links = story.select(".local li")
        source_url = ""
        if source_links:
            # Берём ссылку из первой иконки "копировать ссылку" (обычно это в тегах <li> с title или <a>)
            # В HTML из примера ссылки нет прямой, но если бы была, надо парсить.  
            # Здесь оставим ссылку на сам сюжет, можно улучшить.
            source_url = f"https://thetruestory.news{story.get('href')}"

        results.append({
            "title": title,
            "source_name": source_name,
            "source_url": source_url
        })

    return results

def build_message(stories):
    from datetime import datetime
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    text = f"🗞 ЕЖ. День — главные новости к {now}:\n\n"

    emoji_numbers = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣"]

    for i, story in enumerate(stories):
        number_emoji = emoji_numbers[i] if i < len(emoji_numbers) else f"{i+1}."
        # Формируем строку с ссылкой markdown
        if story["source_url"]:
            text += f"{number_emoji} {story['title']} ([{story['source_name']}]({story['source_url']})).\n\n"
        else:
            text += f"{number_emoji} {story['title']} ({story['source_name']}).\n\n"

    return text

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()

if __name__ == "__main__":
    stories = parse_stories()
    message = build_message(stories)
    print(message)  # Чтобы видеть в логах GitHub Actions
    send_to_telegram(message)
