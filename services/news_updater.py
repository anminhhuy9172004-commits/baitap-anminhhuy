import asyncio

from crawler.news_crawler import crawl_news


UPDATE_INTERVAL = 60


async def news_updater():

    print(
        "[NEWS] Updater started - interval: 60 seconds"
    )

    while True:

        try:

            await asyncio.to_thread(
                crawl_news
            )

        except Exception as error:

            print(
                "[NEWS] Updater error:",
                error
            )

        await asyncio.sleep(
            UPDATE_INTERVAL
        )