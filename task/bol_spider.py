# 电商平台bol爬虫处理器，该平台使用的http2协议，该网站部署了反爬虫机制，需要破解
import json
import logging
import random
import re
import threading
import time
from datetime import datetime, timedelta
from decimal import Decimal

import urllib3
from bs4 import BeautifulSoup
from django.utils import timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync

from task.models import ProductInfo

logger = logging.getLogger(__name__)

# 代理vpn
PROXY_URL = "http://127.0.0.1:8090/"

BASE_URL = 'https://www.bol.com'
CITY_BASE_URL = BASE_URL + '/{}/nl/'

bol_level_1_classify = {"Boeken": "/{}/nl/menu/categories/subMenu/1",
                        "Muziek, Film & Gaming": "/{}/nl/menu/categories/subMenu/2",
                        "Computer & Elektronica": "/{}/nl/menu/categories/subMenu/3",
                        "Speelgoed, Hobby & Feest": "/{}/nl/menu/categories/subMenu/4",
                        "Zwanger, Baby & Peuter": "/{}/nl/menu/categories/subMenu/5",
                        "Mooi & Gezond": "/{}/nl/menu/categories/subMenu/6",
                        "Kleding, Schoenen & Accessoires": "/{}/nl/menu/categories/subMenu/7",
                        "Sport, Outdoor & Reizen": "/{}/nl/menu/categories/subMenu/8",
                        "Kantoor & School": "/{}/nl/menu/categories/subMenu/12",
                        "Eten & Drinken": "/{}/nl/menu/categories/subMenu/10",
                        "Wonen, Koken & Huishouden": "/{}/nl/menu/categories/subMenu/11",
                        "Klussen, Tuin & Dier": "/{}/nl/menu/categories/subMenu/9",
                        "Auto, Motor & Fiets": "/{}/nl/menu/categories/subMenu/13"
                        }

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-en",
    "referer": "https://www.bol.com/nl/nl/",
    "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}


# url = BASE_URL.format(city)
# proxy = urllib3.ProxyManager(PROXY_URL)
# response = proxy.request(method="GET", url=url, headers=headers)
# print(response.status)
# # response = requests.get(url, headers=headers, proxies=proxies)
# # if response.status_code != 200:
# #     print(response.text)
# #     return
# soup = BeautifulSoup(response.text, 'html.parser')
# button = soup.find('button', id_='radix-:Rotar5:-trigger-categories')
# # 获取button之后的所有同级div
# sibling_divs = button.find_next_siblings('div')
# category_first_div = sibling_divs[0]
# a_list = category_first_div.find_all('a')
# for a in a_list:
#     href_id = a.get("href")
#     print(href_id)

#
# async def parser_page_product(product_search_url: str, city: str, product_sort: int, level_1_name, level_2_name,
#                               leve_3_name, category_name, product_main_image):
#     """这个方法只执行一次，为了拿到所有的一级菜单"""
#     product_url = BASE_URL + product_search_url
#     # 商品详情有反扒
#     async with sync_playwright() as p:
#         browser = await p.chromium.launch(headless=False)  # 这里可以headless=True，但是bol更容易检测，建议调试先开着
#         context = await browser.new_context()
#         page = await context.new_page()
#         # 应用 stealth（关键！！！）
#         await stealth_sync(page)
#         try:
#             # 访问页面
#             await page.goto(product_url, timeout=random.randint(10000, 20000))
#             # 增加等待页面加载完成
#             await page.wait_for_load_state('networkidle')
#             # 有时会弹窗，先处理弹窗
#             handle_popup_if_present(page, "div.modal__window__content.js_modal_content")
#             # 等待关键元素 + 随机滚动
#             page.wait_for_selector('#mainContent', timeout=3000)
#             for _ in range(random.randint(2, 4)):
#                 page.mouse.wheel(0, random.randint(300, 800))
#                 time.sleep(random.uniform(0.5, 1.5))
#             product = ProductInfo(platform='bol', city=city, platform_product_id=product_search_url,
#                                   collect_time=datetime.now(), product_url=product_url, category_list=category_name,
#                                   ranking=product_sort, product_image=product_main_image, level_1_classify=level_1_name,
#                                   level_2_classify=level_2_name, level_3_classify=leve_3_name)
#             # 获取页面内容
#             html = page.content()
#             soup = BeautifulSoup(html, 'html.parser')
#             # 解析产品标题
#             product_title_h1 = soup.find_all('h1', class_='page-heading')
#             product_title_span = product_title_h1[0].find_all('span', class_='u-mr--xs')
#             product.title = product_title_span[0].get_text()
#             # 解析描述详情
#             description_div = soup.find('div', attrs={'data-test': 'description'}, class_='product-description')
#             description_p_list = description_div.find_all('p')
#             description = ''
#             for desc_p in description_p_list:
#                 description = description + desc_p.get_text()
#             product.desc = description
#             image_ol = soup.find_all('ol', class_='filmstrip ')[0]
#             image_li_list = image_ol.find_all('li')
#             # 设置所有的图片
#             for i, li in enumerate(image_li_list[1:11], start=1):
#                 image_url = li.find_all('img')[0].get('src')
#                 setattr(product, f'image_{i}', image_url)
#             # 设置评论
#             comment_div = soup.find('div', class_='reviews-summary__avg-score')
#             comment_num_div = soup.find('div', class_='reviews-summary__total-reviews')
#             if comment_div is not None:
#                 product.grade = Decimal(comment_div.get_text())
#             if comment_num_div is not None:
#                 num_text = comment_num_div.get_text()
#                 # 使用正则提取所有数字
#                 numbers = re.findall(r'\d+', num_text)
#                 if len(numbers) > 0:
#                     product.comment_num = int(numbers[0])
#             # 设置价格
#             price_span = soup.find('span', class_='promo-price')
#             if price_span is not None:
#                 round_price = price_span.get_text()
#                 fraction = price_span.find('sup', class_='promo-price__fraction')
#                 if fraction is not None:
#                     price = round_price + '.' + fraction.get_text()
#                 else:
#                     price = round_price + '.00'
#                 product.price = Decimal(price)
#             product.save()
#         except Exception as e:
#             logger.error(f"Error: {e}")
#             page.screenshot(path="linux_error.png")
#         finally:
#             await browser.close()

def handle_route(route, request):
    # 复制原始请求头并设置自定义 header
    headers = request.headers.copy()
    headers[
        "accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    headers[
        "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    headers[
        "cookie"] = "BUI=019f7689-b255-49f8-b044-8ad433641df9; bltgSessionId=7633dad9-feaf-455f-a6be-5a5c8bb18576; XSRF-TOKEN=4aa07d76-bff5-45ef-b3a1-42d4880b6cb6; s_fid=7841BE27611E2A17-070296DD0CEC98C2; px_page=no%20cms%20page; s_cc=true; XSC=wfaQd009tZZMV7UJLHYtPzY0YlGWEUmC; s_vi=[CS]v1|34024DFC4466FF77-400002C9D76FF664[CE]; _ga=GA1.1.1617478936.1745132542; _gcl_au=1.1.1459054733.1745132542; _fbp=fb.1.1745132542711.853099959868575117; fdbk=2; locale=NL; language=nl-NL!; px_bo=1; ga_client_id=1617478936.1745132542; px_prop36=xlarge; _abck=8293C256BFD25C302ADE3651837D838F~-1~YAAQHxQgF38gsHeWAQAAhZNxkQ3jVQ5h87vzFfaZFxTdavf1+qLobIcJBDKihJSD4yLv4K68WAst/5ovk4AO5xfKnf7M0Cfbm4KgSCF18RYlMVZ9M0uUR7RMpO4y+eVFVmOs9+vrNRxvOqSJpnNpy05rjWwUa42SokD0SSB4tAIQF8eCKq2wTo/IfzH7V7v54A53PUMl2oqnOS6sMqCFcMSfH2IKhEWZV5FrGNFPARRspC7YqDPh5HjKTtM6NjpgAI57eGgZHcHYwjg5AX+pfg2NmXWqXfn9CRRqA98e1A2bG9oKRf8SVAnrTgiU7Sx3BA3f8Btmn4DewN4FhsiuK6ZlQOzLjGvKDhajeKfq61mlcOblMwtKL4EwDrODyZntctI7ud1XvgAJoq7Hx7+W3aRpAJZ0XuxepqzZ7KOELiBfiopWAc2UDg==~-1~-1~-1; ak_bmsc=457E71FA571D35E96529E9C38EFFF030~000000000000000000000000000000~YAAQHxQgF4AgsHeWAQAAhZNxkRttOO6QMYPVwA0gNn1Rh2I4mQxjwxkccpg6o9DSTePAlE90jhb5Znb9qe39yScTbVCmhVF/19kenuXK8bxeT28+LkkgeelUGkbh62OaIxWkZLNJfMuvW19mcUhyJWwkDXPuvSipmawixDB2JEN1/hmAL73hvBIFYD6WgAxKvqeIOr20w8SP3WwyfAobQ+XEYO0TiZrHBjrZIQLAr5kZJqr/JVKXB7Z2RNmF2SNN71Vvq3zaHOTuQWCRvovKLSw9Bv4tQWRgWhY4G8Qh+z1jZDmDzmWRR8Al1Yy6VWBoa1CLaZVzLYa9ohCm2VTOCux6ttjLlWs+ENiNWkPtDeZziZ3kj3n4bsAh7csS02IryBA8W4tMixE=; shopping_session_id=65ccd0e52f57cee4c974809458641083a8de4dec6995c451a89b08d896e99971; bolConsentChoices=source#OFC|version#6|int-tran#true|ext-tran#true|int-beh#true|ext-beh#true; sbsd_c=4~1~697037925~plvnrBfS5Ep8mQ8mxwLSdQ6ekDTh9hv1wtwtPkGjKNiaHIUHUhe7XXfkAhcVYg0RwYiXR71v3I6pV5vcr7uEvDprCtAiwC8zmR85BZRu2mOhLWRhu1FrGL1VVZtJRV6fmD1vwVMv/M2lmf1b4e7+BTbDxIuQAu2EsaGFFHHdkCclFPEhfij9CCi7Vvnq6ZloxlRA8RM3zx0QjcA/irOxcuOzsnc7vMS8UeJlhjZ1OxBuj4tZhyeF0F3B7s5pytCCgdozDnJjiejCQu/TyAbiB3P6V62KmB5hK5zrKFYJPhBWw=; px_visit=1; ga_session_id=1746201994; px_eVar14=Browse; px_prop34=aisle; px_pp=Catalog%3Abooks%3Aobject-homepage; px_ppp=basic; __eoi=ID=24f4cf212a1ec615:T=1745132542:RT=1746202413:S=AA-AfjZ6D66H0mcnbl3w2gsJJZq1; sbsd_o=718235C1679D0AF8657FF03D863664930B8E24B8B2FD8F2851E9F2564B77F076~sRvWLx6IHRgzjT3ZDNBce7kN3PewWGXxHunmUi/OfH53JhMewKX6Dp3x1cI61S0p0/RVjaB7sIhBRd0NmjRDoJqFhocrl1WAGDxzDpwl8Bx+1kBz/iaF5YCRS5lAKyjjWgXt0LsSuGOUqQJx3EJmbf9O7VIvd3i87H7kQ86/uAnSqPVPhXQ9D7TyoUgJ+QZS695yGKY+7pYj1qKnrka8WtbdCpMVxPK1CHvjKmtia9sM=; bm_lso=718235C1679D0AF8657FF03D863664930B8E24B8B2FD8F2851E9F2564B77F076~sRvWLx6IHRgzjT3ZDNBce7kN3PewWGXxHunmUi/OfH53JhMewKX6Dp3x1cI61S0p0/RVjaB7sIhBRd0NmjRDoJqFhocrl1WAGDxzDpwl8Bx+1kBz/iaF5YCRS5lAKyjjWgXt0LsSuGOUqQJx3EJmbf9O7VIvd3i87H7kQ86/uAnSqPVPhXQ9D7TyoUgJ+QZS695yGKY+7pYj1qKnrka8WtbdCpMVxPK1CHvjKmtia9sM=^1746202494853; sbsd=sx5PB0IXubu03PtRWVONKKqgUWSXhDB7n/hrJ3exNyZmqd+fl5lZ+AHtDVMzirw0NAqDU4XvOMdzkcugY+nGnCE0OHO3SNw31+hWJlz/XTm328pJx6GC6ZPgRzgg2n1R9CdHZM2t0aSIMWuSOW2egQBntcrKOZJvMtCmLASvYYXWsyQnjS/NSoV+eBjW7X+Oip8S5woyErGoLOy+YqGaC9q40KiazCbjIqeIl2gSejh7SLN6iYL+ykj5TepKT+b/sL41zTzilcjhRP6ETUaQu2pWt9fkh9rWRsOejlStS3grqgqE/XBnislvDiSkZFmwpRr8jc7PW65iOkag51AIcpgsjJxqltXU1UgjW858LYla4/6XIFPO/lcO38adr6sUrcF6WV7MRMcUq16x8wjHiRAx3jTfaI0SJd9y+PSgfdh8=; bm_sz=A223569CA8419D1ED4CB1D28B4F7893B~YAAQDxQgF/JuYYSWAQAAYpPHkRv3WcXjW2f31PsIZ+w13/eu5XHCLWzLw2CCTPwzLWNx++qGd2pxsGW8XrtPTJV5qeUzbO/TBIFWHPiuSveko2lYtKsoW3SZCn+moInclvLrSV2DdPEp58fxNkqO0yWfGtneYojmEtyS6rTwlTnRlk9tME5zM7uC2juQ0pL8F3OgNwv6VAYFnbon5qGuNQQCYEnLQqp5vvSLQqIrGfOq7eCH5B3ZEyCUzF/bIGRQTiUsjP+pIer0tTIJ5EEfBK5CDsRRSK93tPNmyy0hF14GPcMnIwzba2oEeJ+gSd1EWjkZgu2JkG0qczIe8xdrwND87OX/l3YmzL2A+DjgD9hy7gqmbgB7jQEZJ6P4gccko6YzscpzZD2pnE2M9j41CY1eaDJ+DlCXUIZHVe1JlcchGz7xWs9B1/wXQAWtzmiMUv26ciFDSy1awlxGYuqYzWVNTsnrtUTouKkfOXlvDwDhnbAxYFKC0BH2iebEENsR2rydq5opEIZa/wn+xuIOL8HiF/kCrXSPrSO4VpKM~3552824~3752240; px_nr=1746202499760-Repeat; px_eVar80=%7B%22journey%22%3A10%2C%22page%22%3A4%7D; _ga_MY1G523SMZ=GS1.1.1746201994.33.1.1746202500.52.0.0; P=.wspc-deployment-78d6849569-z4fmh; bm_sv=F8A16F2497501123CA159DDD41ED960A~YAAQDxQgF2BvYYSWAQAAhKHHkRtcRQPnYeN2pU0ZGMl2vNpdChl3mGKZlMXl4aAlMwXJ8maL+NAIo0WCiAY4cLZs5NkS//dEkyKDU70X8kux8ve1uNDuCDWmYYez0jtJUUyecd5r928FOcdxY8FyeqeddOcKym3O1YGcva3ezLOkUVZONDw/b2NbEro07lVezSAurT+99LBpy/HncocF2hc7Wj8oKtq4gPKA9BgbGscwDTVu8B1Z+2j07kW86A==~1"

    # 继续请求并带上新的 headers
    route.continue_(headers=headers)


def create_route_handler(cookie_header):
    def handle_route(route, request):
        # 复制原始请求头并设置自定义 header
        headers = request.headers.copy()
        headers[
            "accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        headers[
            "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        headers[
            "cookie"] = cookie_header
        # 继续请求并带上新的 headers
        route.continue_(headers=headers)

    return handle_route


def spider_data(level_1_name: str, level_1_url: str, city: str):
    # 顶级类目分类
    level_2_and_level_3_map = {}
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # 家居装饰和家具
    url = BASE_URL + level_1_url.format(city)
    proxy = urllib3.ProxyManager(PROXY_URL)
    response = proxy.request(method="GET", url=url, headers=headers)
    if response.status != 200:
        logger.error(f'请求发生异常：{str(response.data)}')
        return
    soup = BeautifulSoup(str(response.data), 'html.parser')
    # 找到 main#mainContent
    main_content = soup.find('main', id='mainContent')
    # 二级类目包含三级类目
    target_div = main_content.find_all("div", class_='wsp-sub-nav--sub-menu-tree--child')
    for div in target_div:
        ul = div.find('ul')
        li_list = ul.find_all('li')
        level_2_name = None
        leve_3_list = []
        for li in li_list:
            level_2 = li.find('strong', class_='wsp-sub-nav--parent-title')
            if level_2:
                level_2_name = level_2.get_text()
            a = li.find('a')
            if a:
                level_3_href = a.get('href')
                leve_3_name = (a.find('p', class_='wsp-sub-nav--link-text').get_text().replace('\\n', '')
                               .replace("\n", "").replace("\r", ""))
                leve_3_list.append({'leve_3_name': leve_3_name, 'level_3_href': level_3_href})
        level_2_and_level_3_map[level_2_name] = leve_3_list
    for level_2_name, level_3_list in level_2_and_level_3_map.items():
        # 模拟打开浏览器，使用代理
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False,
                                        args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(proxy={"server": PROXY_URL})
            base_url = CITY_BASE_URL.format(city)
            try:
                # 模拟获取cookie
                cookie_page = context.new_page()
                # 请求目标页面
                cookie_page.goto(base_url, wait_until="networkidle", timeout=30000)
                cookie_page.wait_for_load_state("networkidle")
                cookie_page.wait_for_selector('body', timeout=10000)
                dialog = cookie_page.wait_for_selector('div[role="dialog"]',
                                                       timeout=random.randint(2000, 10000))
                if dialog:
                    logger.info("dialog exist ,auto click button...")
                    buttons = dialog.query_selector_all("button")
                    first_button = buttons[0]
                    # 模拟移动鼠标到按钮上
                    first_button.hover()
                    time.sleep(random.uniform(0.5, 1.5))  # 给点缓冲时间
                    first_button.click()
                    logger.info("dialog has click button")

            except Exception as e:
                logger.info(f"no dialog ,continue do process... {e}")
            cookies = cookie_page.context.cookies()
            cookie_list = []
            for cookie in cookies:
                cookie_list.append(cookie['name'] + '=' + cookie['value'])
            cookie_header = '; '.join(cookie_list)
            # 等待加载结束（可按需调整）
            cookie_page.wait_for_timeout(2000)
            for level_3 in level_3_list:
                level_3_href = level_3.get('level_3_href')
                leve_3_name = level_3.get('leve_3_name')
                # 默认按照热销排序
                page_size = 1
                # 只爬取100页
                product_sort = 0
                while page_size <= 1:
                    if page_size == 1:
                        page_url = BASE_URL + level_3_href + '?sort=popularity1'
                    else:
                        page_url = BASE_URL + level_3_href + f'?sort=popularity1&page={page_size}'
                    # 商品页有反扒, 这里可以headless=True，但是bol更容易检测，建议调试先开着，args参数：减少被网站检测为自动化工具（如爬虫）的概率
                    page = context.new_page()
                    # 拦截所有请求并应用自定义 headers
                    page.route("**/?sort=popularity1", create_route_handler(cookie_header))
                    # stop_on_refresh(page, page_url)
                    # 应用 stealth（关键！！！）
                    stealth_sync(page)
                    # 拦截掉 bol 的反爬检测请求（非常重要！）
                    # page.route("**/.well-known/sbsd/**", lambda route: route.abort())
                    try:
                        logger.info(f'goto page :{page_url}')
                        # 访问页面
                        # product_page.goto(product_url, wait_until="load")，这是指：等待“load”事件被触发后再继续执行代码，相当于浏览器 window.onload 事件完成。
                        # 这通常意味着：HTML 文档和其依赖的资源（如图片、CSS）都已加载；但并不保证页面的 JavaScript 异步请求（XHR/fetch）已完成。
                        # product_page.wait_for_load_state("networkidle")
                        # 这是指：等页面网络活动接近“空闲”状态（500ms 内无网络请求）才继续执行代码，通常更严格，用于等待 Ajax 请求或懒加载数据的页面。
                        page.goto(page_url, wait_until="networkidle", timeout=30000)
                        time.sleep(random.randint(10, 15))
                        page.wait_for_load_state("networkidle")
                        # 有时会弹窗，先处理弹窗
                        handle_popup_if_present(page, 'body.modal--is-open')
                        # 等待关键元素 + 随机滚动
                        page_div = page.wait_for_selector('#js_list_view', timeout=random.randint(10000, 20000))
                        if not page_div:
                            continue
                        # 获取页面内容
                        html = page.content()
                        # page.close() 最后在关闭，此时不要关闭
                        if not html:
                            continue
                        smooth_scroll(page)
                        soup = BeautifulSoup(html, 'html.parser')
                        category_name = soup.find_all('h1', class_='h1 bol_header')[0].get_text()
                        product_ul = soup.find_all('ul', class_='product-list')
                        product_li = product_ul[0].find_all('li', class_='product-item--row')
                        for li in product_li:
                            li.get('data-id')
                            li.get('data-bltgi')
                            product_a = li.find('a', class_='product-image')
                            product_url = product_a.get('href')
                            logger.info(f'product_url: {product_url}')

                            product_url = BASE_URL + product_url
                            product_page = context.new_page()
                            try:
                                # 访问页面
                                product_page.goto(product_url, wait_until="load", timeout=random.randint(10000, 20000))
                                # # 增加等待页面加载完成
                                # product_page.wait_for_load_state('networkidle')

                                handle_popup_if_present(product_page,
                                                        'div.modal__window.js_modal_window[role="dialog"]')
                                # mouse_move(product_page)
                                # 等待关键元素 + 随机滚动
                                product_page.wait_for_selector('#mainContent', timeout=3000)
                                viewport_size = product_page.viewport_size
                                height = viewport_size['height']
                                smooth_scroll(page=product_page, total_distance=random.randint(600, height))

                                product = ProductInfo(platform='bol', city=city,
                                                      platform_product_id=product_url,
                                                      collect_time=datetime.now(), product_url=product_url,
                                                      category_list=category_name,
                                                      ranking=product_sort,
                                                      level_1_classify=level_1_name, currency='EUR',
                                                      level_2_classify=level_2_name, level_3_classify=leve_3_name,
                                                      create_time=datetime.now(), update_time=datetime.now())
                                # 获取页面内容
                                product_html = product_page.content()
                                soup = BeautifulSoup(product_html, 'html.parser')
                                # 遍历是否有多sku
                                # sku_options = soup.find('div', class_='feature-options')
                                # 等待目标父容器加载
                                sku_options = soup.find('div', class_='feature-options')
                                if sku_options:
                                    # sku 分为下拉选形式的，和单选形式的
                                    # 1.单选形式处理
                                    sku_single_choice = product_page.locator("div.feature-options a.feature-option")
                                    if sku_single_choice and sku_single_choice.count() > 0:
                                        parse_sku_options(sku_single_choice, product, context)
                                    # 2.下拉选形式处理
                                    sku_list = product_page.locator("div.feature-options a.feature-list__item")
                                    if sku_list and sku_list.count() > 0:
                                        parse_sku_list(sku_list, product, context)
                                else:
                                    parse_brand(soup, product)
                                    parse_product_ean(product_page, product)
                                    product_main_image = soup.find('img',
                                                                   attrs={'data-test': 'product-main-image'}).get(
                                        'src')
                                    product.product_image = product_main_image
                                    parse_discount_price(soup)
                                    original_price = parse_discount_price(soup)
                                    parse_product(product, soup, original_price)
                            except Exception as e:
                                logger.error(f'parse product error:{e}')
                            finally:
                                product_page.close()
                            product_sort += 1
                    except PlaywrightTimeoutError as e:
                        logger.error(f"wait page timeout or element not exist: {e}")
                    except Exception as e:
                        logger.error(f"Error: {e}")
                    finally:
                        page.close()
                        pass
                    page_size += 1
            browser.close()


def parse_brand(soup, product):
    """设置产品品牌"""
    brand = soup.find("div", attrs={'data-test': 'brand'})
    if not brand:
        return
    brand_a = brand.find('a', attrs={'data-role': 'BRAND'})
    if not brand_a:
        return
    brand = brand_a.get_text()
    product.brand = brand


def parse_sku_list(sku_list, product, context):
    """处理list项sku"""
    sku_count = sku_list.count()
    for i in range(sku_count):
        try:
            # 点击刷新页面，需获取刷新后的页面的数据
            sku = sku_list.nth(i)
            # 使用 CSS 选择器获取内部 span（基于 DOM 层级）
            text_span = sku.query_selector('.feature-list__text span')
            sku_name = text_span.inner_text()
            product.sku = sku_name
            sku_url = sku.get_attribute('href')
            sku_page = context.new_page()
            sku_page_url = BASE_URL + sku_url
            sku_page.goto(sku_page_url, wait_until="load", timeout=20000)
            # 等待关键元素 + 随机滚动
            sku_page.wait_for_selector('#mainContent', timeout=3000)
            value = random.choice([True, False])
            if value:
                viewport_size = sku_page.viewport_size
                height = viewport_size['height']
                smooth_scroll(page=sku_page, total_distance=random.randint(600, height))
            sku_html = sku_page.content()
            sku_soup = BeautifulSoup(sku_html, 'html.parser')

            product_main_image = sku_soup.find('img',
                                               attrs={
                                                   'data-test': 'product-main-image'}).get(
                'src')
            parse_brand(sku_soup, product)
            parse_product_ean(sku_page, product)
            product.product_image = product_main_image
            original_price = parse_discount_price(sku_soup)
            parse_product(product, sku_soup, original_price)
        except Exception as e:
            logger.error(f'sku page parser error:{e}')
        finally:
            sku_page.close()


def parse_sku_options(sku_list, product, context):
    """处理单选项sku"""
    sku_count = sku_list.count()
    for i in range(sku_count):
        try:
            # 点击刷新页面，需获取刷新后的页面的数据
            sku = sku_list.nth(i)
            sku.hover()
            time.sleep(random.uniform(0.5, 1.5))  # 给点缓冲时间

            sku_name = sku.get_attribute("title")

            sku_class = sku.get_attribute("class")
            if "feature-option--btn" in sku_class:
                sku_name = sku.get_attribute("title")
            if "feature-option--image" in sku_class:
                try:
                    sku_image = sku.locator("img")
                    if sku_image:
                        alt_text = sku_image.get_attribute("alt")
                        sku_name = alt_text
                except Exception as e:
                    logger.warning(f'sku image not exist: {e}')
            if not sku_name:
                sku_name = sku.get_attribute("data-test")
            product.sku = sku_name
            sku_url = sku.get_attribute('href')
            sku_page = context.new_page()
            sku_page_url = BASE_URL + sku_url
            sku_page.goto(sku_page_url, wait_until="load", timeout=20000)
            # 等待关键元素 + 随机滚动
            sku_page.wait_for_selector('#mainContent', timeout=3000)
            value = random.choice([True, False])
            if value:
                viewport_size = sku_page.viewport_size
                height = viewport_size['height']
                smooth_scroll(page=sku_page, total_distance=random.randint(600, height))
            sku_html = sku_page.content()
            sku_soup = BeautifulSoup(sku_html, 'html.parser')

            product_main_image = sku_soup.find('img',
                                               attrs={
                                                   'data-test': 'product-main-image'}).get(
                'src')
            parse_brand(sku_soup, product)
            parse_product_ean(sku_page, product)
            product.product_image = product_main_image
            original_price = parse_discount_price(sku_soup)
            parse_product(product, sku_soup, original_price)
        except Exception as e:
            logger.error(f'sku page parser error:{e}')
        finally:
            sku_page.close()


def parse_product_ean(page, product):
    """解析产品信息的ean"""
    # 找到 EAN 的 h3 元素
    ean_header = page.locator("h3", has_text="EAN")
    if not ean_header:
        return
    # 获取其父 div.specs 元素
    specs_div = ean_header.locator("xpath=..")  # 向上一级
    if not specs_div:
        return
        # 找到 div 中的 dl
    dl_element = specs_div.locator("dl.specs__list")
    dd_element = dl_element.locator("dd").first
    if not dd_element:
        return
    ean = dd_element.inner_text()
    product.ean = ean


def parse_discount_price(soup):
    """处理折扣信息"""
    try:
        discount_div = soup.find('div', class_='ab-discount')
        if discount_div:
            original_price = discount_div.find('del').get_text()
            price_list = re.findall(r'\d+', original_price)
            if len(price_list) == 1:
                original_price = str(price_list[0]).strip() + '.00'
            elif len(price_list) == 2:
                original_price = str(price_list[0]).strip() + '.' + str(price_list[1]).strip()
            else:
                return None
            logger.info(f'original price: {original_price}')
            price = Decimal(original_price)
            return price
        return None
    except Exception as e:
        logger.error(f"parse_discount_price :{e}")
        return None


def parse_product(product, soup, original_price):
    # 解析产品标题
    product_title_h1 = soup.find_all('h1', class_='page-heading')
    product_title_span = product_title_h1[0].find_all('span', class_='u-mr--xs')
    product.title = product_title_span[0].get_text()
    # 解析描述详情
    description_div = soup.find('div', attrs={'data-test': 'description'},
                                class_='product-description')
    description_p_list = description_div.find_all('p')
    description = ''
    for desc_p in description_p_list:
        description = description + desc_p.get_text()
    product.desc = description
    image_ol_div = soup.find('div', class_='filmstrip-viewport')
    if image_ol_div:
        image_ol = image_ol_div.find('ol', class_='filmstrip')
        image_li_list = image_ol.find_all('li')
        # 设置所有的图片
        for i, li in enumerate(image_li_list[:10]):
            image_url = li.find_all('img')[0].get('src')
            setattr(product, f'image_{i + 1}', image_url)
    # 设置评论
    comment_div = soup.find('div', class_='reviews-summary__avg-score')
    comment_num_div = soup.find('div', class_='reviews-summary__total-reviews')
    if comment_div is not None:
        product.grade = Decimal(comment_div.get_text().strip().replace(",", "."))
    if comment_num_div is not None:
        num_text = comment_num_div.get_text()
        # 使用正则提取所有数字
        numbers = re.findall(r'\d+', num_text)
        if len(numbers) > 0:
            product.comment_num = int(numbers[0])
    # 设置价格
    price_span = soup.find('span', class_='promo-price')
    if price_span is not None:
        round_price = price_span.get_text()
        price_list = re.findall(r'\d+', round_price)
        if price_list:
            if len(price_list) == 1:
                price = str(price_list[0]).strip() + '.00'
            elif len(price_list) == 2:
                price = str(price_list[0]).strip() + '.' + str(price_list[1]).strip()
            logger.info(f'price: {price}')
            product.price = Decimal(price)
            if original_price:
                product.original_price = original_price
                product.discount = Decimal(original_price) - Decimal(price)
        else:
            product.price = None
            product.original_price = None
            product.discount = None
            logger.error('can not parser price_list span')
    else:
        product.price = None
        product.original_price = None
        product.discount = None
        logger.warning('can not parser price span')
    # 在主线程中调用保存操作，同步保存会报错
    threading.Thread(target=save_product, args=(product,)).start()
    time.sleep(random.uniform(1, 3))


def stop_on_refresh(page, target_url):
    """判断页面是不是存在刷新，bol有监测机制，多次刷新后就会报错，封ip"""

    def on_navigation(frame):
        if frame.url == target_url:
            # 页面正在被刷新，立即中断
            raise Exception("Page is refreshing, aborting...")

    page.on("framenavigated", on_navigation)


def save_product(product):
    three_days_ago = timezone.now() - timedelta(days=3)

    """通过异步线程去保存，同步保存会报错"""
    try:
        product.pk = None
        exist_record = ProductInfo.objects.filter(platform_product_id=product.platform_product_id,
                                                  sku=product.sku,
                                                  create_time__gte=three_days_ago).first()
        if exist_record:
            logger.warning(f'product record has save three day before, not need save again!')
            return
        product.save()
    except Exception as e:
        logger.error(f'product save error: {e}')


def mouse_move(page):
    """模拟鼠标在页面上进行移动"""
    # 获取页面宽高
    viewport_size = page.viewport_size
    width = viewport_size['width']
    height = viewport_size['height']

    # 模拟随机鼠标移动
    # for _ in range(random.randint(2, 7)):
    x = random.randint(0, width)
    y = random.randint(0, height)
    page.mouse.move(x, y, steps=random.randint(5, 15))  # steps 越大越平滑
    time.sleep(random.uniform(0.1, 0.3))


def mouse_move_wheel(page):
    """模拟页面滚动"""
    scroll_amount = random.randint(300, 800)
    page.mouse.wheel(0, scroll_amount)  # 向下滚动
    time.sleep(random.uniform(0.1, 0.5))  # 增加停顿，更像人


def smooth_scroll(page, total_distance=600, step=100, delay_range=(0.0, 0.2)):
    """
    模拟鼠标平滑滚动

    :param page: Playwright 页面对象
    :param total_distance: 总滚动距离（px）
    :param step: 每次滚动的像素步长
    :param delay_range: 每次滚动后的等待时间范围（秒）
    """
    current = 0
    while current < total_distance:
        scroll_amount = min(step, total_distance - current)
        page.mouse.wheel(0, scroll_amount)
        current += scroll_amount
        time.sleep(random.uniform(*delay_range))


def handle_popup_if_present(page, div_class):
    """判断是否存在弹窗，存在弹窗时关闭弹窗"""
    try:
        dialog = page.wait_for_selector(div_class,
                                        timeout=random.randint(2000, 3000))
        if dialog:
            logger.info("dialog exist ,auto click button...")
            button = dialog.query_selector("#js-first-screen-accept-all-button")
            # 模拟移动鼠标到按钮上
            button.hover()
            time.sleep(random.uniform(0.5, 1.5))  # 给点缓冲时间
            button.click()
            logger.info("dialog has click button")

    except PlaywrightTimeoutError:
        logger.info("no dialog ,continue do process...")


def home_page_spider(url: str = 'https://www.bol.com/nl/nl'):
    """
    爬取首页所有一级分类数据的，该操作比较麻烦，可以爬取后就不在修改了，后续如果还要修改则调用改函数即可
    该网站的反爬机制很厉害，没办法直接通过静态页面去
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)  # 这里可以headless=True，但是bol更容易检测，建议调试先开着
        # context = browser.new_context()
        context = browser.new_context(proxy={"server": PROXY_URL})
        page = context.new_page()

        # 应用 stealth（关键！！！）
        stealth_sync(page)

        try:
            # 访问页面
            page.goto(url, timeout=60000)
            # 增加等待页面加载完成
            page.wait_for_load_state('load')
            # 有时会弹窗，先处理弹窗
            handle_popup_if_present(page, "div.modal__window__content.js_modal_content")
            # 等待关键元素 + 随机滚动
            page.wait_for_selector('.bg-neutral-background-low', timeout=30000)
            for _ in range(3):
                page.mouse.wheel(0, random.randint(300, 800))
                time.sleep(random.uniform(0.5, 1.5))

            # 获取页面内容
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            menu_div_list = soup.find_all('section', class_='bg-neutral-background-low')
            menu_div = menu_div_list[0]
            hidden_menus = menu_div.find_all('div', attrs={'hidden': True})
            level_1_menu = hidden_menus[0].find_all('a')
            for a in level_1_menu:
                print(a.get("href"))
                bol_level_1_classify[a.get_text()] = a.get("href")

            print(json.dumps(bol_level_1_classify))
            return bol_level_1_classify
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="linux_error.png")
        finally:
            browser.close()

#
# if __name__ == "__main__":
#     # 默认新西兰
#     default_city = 'nl'
#     # bol_level_1_classify = home_page_spider(CITY_BASE_URL.format(city))
#     spider_data('Boeken', bol_level_1_classify['Boeken'], default_city)
