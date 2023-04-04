import scrapy
from bs4 import BeautifulSoup
from datetime import datetime
import csv


class QnaSpider(scrapy.Spider):
    name = "qna"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://www.naver.com"
        self.start_urls = [self.base_url]
        self.expert_ids = []
        with open("experts.csv") as fr:
            reader = csv.reader(fr)
            for row in reader:
                self.expert_ids.append(row[0])
        self.expert_ids = self.expert_ids[:100]
        self.output_file = open("qna.csv", "w")
        self.output_writer = csv.writer(self.output_file)
        self.expert_answer_url = "https://kin.naver.com/userinfo/expert/answerList.naver"

    def spider_closed(self, spider):
        self.output_file.close()

    def parse(self, response):
        for i in range(len(self.expert_ids)):
            url = f"{self.expert_answer_url}?{self.expert_ids[i]}"
            req = scrapy.Request(
                url=url,
                callback=self.parse_list_page
            )
            yield req

    def parse_list_page(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        answer_num = soup\
            .find("dl", class_="mykin_num")\
            .find_all("dd")[0].text
        answer_num = int(answer_num)
        # 답변이 너무 적거나, 비정상적으로 많으면 필터링
        if answer_num < 5 or answer_num > 3000:
            return

        # 최근 답변부터 100개 페이지 요청
        self.output_writer.writerow([answer_num])
        # pro_list = soup.find("ul", class_="pro_list").find_all("li")
        # for pro in pro_list:
        #     pro_soup = BeautifulSoup(str(pro), "lxml")
        #     link = pro_soup.find("a").get("href")
        #     self.output_writer.writerow([link.split("?")[-1]])
