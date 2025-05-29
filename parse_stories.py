import requests
from bs4 import BeautifulSoup
import os

URL = "https://thetruestory.news/ru/russia"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

def parse_stories():
    response = requests.get(URL)
    response.raise_for_status()

    # Сохраняем страницу в файл для проверки
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("HTML страницы сохранён в page.html")

    soup = BeautifulSoup(response.text, "html.parser")

    stories = soup.find_all("a", class_="s2 story illustrated")
    print(f"Найдено сюжетов: {len(stories)}")

    results = []

    for story in stories[:7]:
        headline = story.select_one(".s2.message.headline.pinned h2")
        title = headline.get_text(strip=True) if headline else "Без заголовка"

        first_message_source = story.select_one(".s2.message.headline.pinned .s2.source")
        source_name = first_message_source.get_text(strip=True) if first_message_source else ""

        source_url = ""
        if story.get("href"):
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

    if not stories:
        text += "Новостей не найдено."

    for i, story in enumerate(stories):
        number_emoji = emoji_numbers[i] if i < len(emoji_numbers) else f"{i+1}."
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
    print("Сообщение отправлено в Telegram")

if __name__ == "__main__":
    stories = parse_stories()
    message = build_message(stories)
    print(message)  # Выводим в логи
    send_to_telegram(message)
