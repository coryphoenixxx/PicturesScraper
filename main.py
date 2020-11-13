import time, random
import requests
import os, sys
from termcolor import cprint
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent


DIR = "JoyReactor"
URL = "http://reactor.cc/best"
UA = UserAgent()


def gen_index():
    i = 1
    while True:
        yield i
        i += 1
gen = gen_index()


def get_last_page_num():
    global URL
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "lxml")
    last_page_num = int(soup.find('div', {'class': 'pagination_expanded'}).find_next().text)
    return last_page_num


def downloader(link):
    global gen
    file_name = f"{DIR}/{next(gen)}.{link.split('.')[-1]}"
    headers = {'User-Agent': UA.random}
    response = requests.get(link, headers=headers)
    with open(file_name, 'wb') as f:
        f.write(response.content)


def get_image(page_index):
    time.sleep(random.random() * random.randint(2, 8))
    start = time.time()

    while True:
        headers = {'User-Agent': UA.random}
        response = requests.get(f'{URL}/{page_index}', headers=headers)
        if response.status_code == 200:
            cprint(f"Thread taking page №{page_index} for processing...", 'green')
            break
        else:
            cprint(f"Thread CAN'T taking page №{page_index} for processing!!! [{response.status_code}]", 'red', attrs=['bold'], file=sys.stderr)
            time.sleep(1)

    soup = BeautifulSoup(response.content, 'lxml')
    posts = soup.find_all('div', {'class': 'post_content'})
    for post in posts:
        [downloader(link['src']) for link in post.find_all('img')]

    cprint(f"    ...page №{page_index} processing completed in {time.time() - start:0.2f} sec", 'grey')


start = time.time()
if __name__ == "__main__":
    try:
        os.mkdir(DIR)
    except FileExistsError:
        pass

    max = get_last_page_num()

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(get_image, range(1, max))

    print(f"\nTOTAL IMAGES: {next(gen) - 1}")
    print(f"TOTAL TIME: {time.time() - start:0.2f} sec")

