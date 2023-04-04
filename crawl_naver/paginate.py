import csv
from tqdm import tqdm
from typing import List, Tuple


def flush_buffer_to_file(pagenum: int, buffer: List[Tuple[str, str]]):
    output_filename = f"./qna_pages/page_{str(pagenum).zfill(4)}.csv"
    with open(output_filename, "w") as fw:
        writer = csv.writer(fw)
        for row in buffer:
            writer.writerow(row)


def paginate_qna():
    cnt = 0
    pagenum = 0
    pagesize = 1000

    with open("qna.csv") as fr:
        reader = csv.reader(fr)
        buffer: List[Tuple[str, str]] = []
        for row in tqdm(reader, total=120000):
            buffer.append(row)
            cnt += 1
            if cnt % pagesize == 0:
                flush_buffer_to_file(pagenum, buffer)
                buffer = []
                pagenum += 1
        if buffer:
            flush_buffer_to_file(pagenum, buffer)


if __name__ == '__main__':
    paginate_qna()
