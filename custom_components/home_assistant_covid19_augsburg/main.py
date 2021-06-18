from .crawler import CovidCrawler


def main():
    crawler = CovidCrawler()
    result = crawler.crawl()
    print(result)


if __name__ == "__main__":
    main()
