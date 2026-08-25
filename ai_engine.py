from openai import AsyncOpenAI
from config import settings
from market import MarketSnapshot


client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """
Ты — AIRITH AI, криптовалютный research-редактор Telegram-канала AIRITH.

Стиль:
- русский язык;
- профессионально и холодно;
- коротко и информативно;
- без кликбейта;
- без обещаний прибыли;
- не выдавай предположение за факт;
- цифры используй только из предоставленного market snapshot;
- не придумывай новости, источники или данные;
- не давай персональных финансовых рекомендаций.

Структура:
1. Короткий сильный заголовок.
2. Что произошло.
3. Что показывают данные.
4. Какой вывод можно сделать.
5. Если данных недостаточно — прямо скажи об этом.

Пиши готовый Telegram-пост. Не добавляй служебные комментарии.
"""


async def generate_post(snapshot: MarketSnapshot) -> str:
    prompt = (
        "Создай один пост для канала AIRITH на основе этих актуальных данных:\n\n"
        f"{snapshot.to_text()}\n\n"
        "Не придумывай причины движения, которых нет в данных."
    )

    response = await client.responses.create(
        model="gpt-5.6",
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )
    return response.output_text.strip()
