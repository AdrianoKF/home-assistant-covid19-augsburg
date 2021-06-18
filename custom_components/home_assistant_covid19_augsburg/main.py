from home_assistant_covid19_augsburg.crawler import CovidCrawler


def main():
    crawler = CovidCrawler()
    result = crawler.crawl()
    print(result)


if __name__ == "__main__":
    main()
