# 电商平台fruugo爬虫处理器
import logging
import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from task.models import ProductInfo

logger = logging.getLogger(__name__)

BASE_URl = 'https://www.fruugo.co.uk'


def spider_data(identifier: str, city: str):
    # 顶级类目分类

    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # 家居装饰和家具
    url = BASE_URl + identifier
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 查找所有子标签
    child = soup.find_all('div', class_='container pt-16 pt-md-24 pt-lg-32')
    tail_child = soup.find_all('div', class_='container Search pt-16 pt-md-24 pt-lg-32')
    if len(child) == 0 and len(tail_child) == 0:
        raise Exception(f'没有菜单节点也不是最后一层节点，请调整代码')
    if tail_child:
        # 递归到了最后一层，根据最后一层的目录数据，查询商品信息
        page = soup.find('a', class_='d-none d-xl-flex').get_text()
        page = int(page)
        # 查询最热销的商品信息
        product_search_url = url + '?sorting=bestsellingdesc'
        # 开始查询数据
        if page <= 100:
            # 查询page页的数据
            for i in range(page):
                parser_page_product(product_search_url)
        else:
            # 查询一百页的数据
            for i in range(100):
                parser_page_product(product_search_url)
    else:
        for child in child:
            all_links = child.find('div', class_='item-grid mb-48').find_all('a')
            for a in all_links:
                # 递归调用
                href_id = a.get("href")
                logger.info(f'find link: {href_id}')
                spider_data(href_id, 'uk')
    # product = ProductInfo(platform='fruugo', platform_product_id=1, del_flag=False)
    # product.save()
    # logger.info("do spider data scheduler...")


def parser_page_product(product_search_url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # 休眠随机1-5s
    sleep_time = random.uniform(1, 5)  # 生成1-5秒之间的随机浮点数
    logger.info(f"线程休眠 {sleep_time:.2f} 秒")
    time.sleep(sleep_time)
    logger.info("线程继续执行")
    # 遍历这个页面上所有的商品信息
    page_product_response = requests.get(product_search_url, headers=headers)
    page_product_soup = BeautifulSoup(page_product_response.text, 'html.parser')
    page_product = page_product_soup.find_all('div', class_='products-list row')
    for product_page in page_product:
        product_list = product_page.find_all('div', class_='product-item')
        for product in product_list:
            a_label_list = product.find_all('a')
            a_label = a_label_list[0]
            product_url = a_label.get("href")
            image_container = a_label.find('div', class_='product-item-image-container')
            product_image_url = image_container.find('img').get('src')
            desc_container = a_label.find('div', class_='product-item-details')
            product_desc = desc_container.find('div', class_='description-wrapper').find('span',
                                                                                         class_='description').get_text()
            product_info = requests.get(BASE_URl + product_url, headers=headers)
            product_soup = BeautifulSoup(product_info.text, 'html.parser')
            title = product_soup.find('h1', class_='js-product-title').get_text()
            price_content = product_soup.find('meta', attrs={'property': 'product:price:amount'})
            price = None
            if price_content:
                price = price_content.get('content')
            else:
                logger.error(f'未找到价格标签')

            price_currency = product_soup.find('meta', attrs={'property': 'product:price:currency'})
            currency = None
            if price_currency:
                currency = price_currency.get('content')
            else:
                logger.error(f'未找到价格币种')
            desc = product_soup.find('div', class_='Product__Description-text').get_text()
            product = ProductInfo(platform='fruugo', city='uk', platform_product_id=product_url,
                                  product_image=product_image_url, title=title, desc=desc, price=price,
                                  currency=currency, del_flag=False, create_time=datetime.now(),
                                  update_time=datetime.now())
            product.save()


if __name__ == '__main__':
    spider_data('/home-decor-furnishings/d-ws56158702')
