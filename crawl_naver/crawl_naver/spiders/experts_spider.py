import scrapy
from bs4 import BeautifulSoup
from datetime import datetime
import csv


class ExpertsSpider(scrapy.Spider):
    name = "experts"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://kin.naver.com/people/expert/index.naver"
        self.start_urls = [self.base_url]
        # 가져올 전문가 아이디
        self.expert_id = "DOCTOR"
        self.num_pages = 100
        self.output_file = open("experts.csv", "w")
        self.output_writer = csv.writer(self.output_file)

    def spider_closed(self, spider):
        self.output_file.close()

    def parse(self, response):
        # type = DOCTOR & sort = answerDate & page = 50
        url = f"{self.base_url}?type={self.expert_id}&sort=answerDate"
        for i in range(self.num_pages):
            req = scrapy.Request(
                url=f"{url}&page={i+1}",
                callback=self.parse_list_page
            )
            yield req

    def parse_list_page(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        pro_list = soup.find("ul", class_="pro_list").find_all("li")
        for pro in pro_list:
            pro_soup = BeautifulSoup(str(pro), "lxml")
            link = pro_soup.find("a").get("href")
            self.output_writer.writerow([link.split("?")[-1]])
