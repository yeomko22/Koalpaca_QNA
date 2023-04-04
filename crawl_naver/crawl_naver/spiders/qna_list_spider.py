import scrapy
from bs4 import BeautifulSoup
import csv


class QnaListSpider(scrapy.Spider):
    name = "qna_list"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://www.naver.com"
        self.start_urls = [self.base_url]
        self.expert_ids = []
        with open("experts.csv") as fr:
            reader = csv.reader(fr)
            for row in reader:
                self.expert_ids.append(row[0])
        self.output_file = open("qna.csv", "w")
        self.output_writer = csv.writer(self.output_file)
        self.expert_answer_url = "https://kin.naver.com/userinfo/expert/answerList.naver"

    def spider_closed(self, spider):
        self.output_file.close()

    def parse(self, response):
        for expert_id in self.expert_ids:
            url = f"{self.expert_answer_url}?{expert_id}"
            req = scrapy.Request(url=url, callback=self.parse_expert_page)
            req.meta["expert_id"] = expert_id
            yield req

    def parse_expert_page(self, response):
        expert_id = response.meta["expert_id"]
        soup = BeautifulSoup(response.text, "lxml")
        answer_num = soup\
            .find("dl", class_="mykin_num")\
            .find_all("dd")[0].text
        answer_num = int(answer_num)
        # 답변이 너무 적거나, 비정상적으로 많으면 필터링
        if answer_num < 5 or answer_num > 3000:
            return

        # 답변이 10개 이상이면 다음 페이지도 이어서 요청
        paginate = soup.find("div", class_="paginate").find_all("a")
        max_pagenum = min(len(paginate), 10)
        for i in range(max_pagenum):
            url = f"{self.expert_answer_url}?{expert_id}&page={i+1}"
            req = scrapy.Request(url=url, callback=self.parse_list_page)
            req.meta["expert_id"] = expert_id
            yield req

    def parse_list_page(self, response):
        expert_id = response.meta["expert_id"]
        soup = BeautifulSoup(response.text, "lxml")
        board_list = soup.find("tbody", id="au_board_list")
        rows = board_list.find_all("tr")
        for row in rows:
            row_soup = BeautifulSoup(str(row), "lxml")
            doc_url = row_soup.find("td", class_="title").find("a").get("href")
            self.output_writer.writerow([expert_id, "https://kin.naver.com" + doc_url])
