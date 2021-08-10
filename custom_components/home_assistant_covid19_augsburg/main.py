from .crawler import CovidCrawler


async def main():
    crawler = CovidCrawler()
    # result = await crawler.crawl()
    # print(result)

    result = await crawler.crawl_vaccination()
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
