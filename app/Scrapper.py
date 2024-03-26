import requests
from bs4 import BeautifulSoup
import cssutils
from urllib.parse import urlparse


class Scrapper:
    headers = {
        "USer-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Accept-Language": "en"
    }
    url = None
    product_selector = None
    name_selector = None
    price_selector = None
    image_selector = None
    small_image_selector = None
    price_offset = 0
    link_selector = None
    shopName = None

    # shopWebsite = None

    def __init__(self, url, product_selector, name_selector, price_selector, image_selector, link_selector, shopName,
                 price_offset=0):
        self.url = url
        self.name_selector = name_selector
        self.price_selector = price_selector
        self.image_selector = image_selector
        self.product_selector = product_selector
        self.price_offset = price_offset
        self.link_selector = link_selector
        self.shopName = shopName

    def getResult(self):
        req = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(req.text, "lxml")
        # print(soup.prettify())
        name = soup.select_one(selector=self.name_selector).getText()
        name = name.strip()
        price = soup.select_one(selector=self.price_selector).getText()
        price = price.strip()

        image = soup.select_one(selector=self.image_selector).get('src')

        return name, price, image

    def find_str(self, s, char):
        index = 0

        if char in s:
            c = char[0]
            for ch in s:
                if ch == c:
                    if s[index:index + len(char)] == char:
                        return index

                index += 1

        return -1

    def getResultsForMany(self):
        # print(self.url)
        req = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(req.text, "lxml")

        # print(soup.prettify())
        productList = list()
        products = soup.select(selector=self.product_selector)
        # print(products)
        for product in products:
            productDict = dict()
            # Get The Name
            name = product.select_one(selector=self.name_selector).getText()
            productDict['name'] = name.strip()

            # print(name)
            # print()

            # Get the Image
            if product.select_one(selector=self.price_selector) is not None:
                price = product.select_one(selector=self.price_selector).getText()
                # print(price)
                price = price.strip()
                price = price.replace(',', '')
                if self.shopName == "Edgars Stores":
                    price = price.replace('\t', '')
                    price = price.replace('\n', '')
                    price = price.replace(' ', '')
                    price = price.replace('ExTax:ZWL', '')
                    index = int(self.find_str(price, '.')) + 2
                    price = price[:index]
                    # print(price)
                elif self.shopName == "OK Zimbabwe":
                    price = price[:-2] + '.' + price[-2:]
                price = price[self.price_offset:]

                productDict['price'] = price
            else:
                productDict['price'] = 0.00

            # print(product.select_one(selector=self.image_selector))
            image = product.select_one(selector=self.image_selector).get('data-src')

            if image is None:
                image = product.select_one(selector=self.image_selector).get('data-original')

            if image is None:
                image = product.select_one(selector=self.image_selector).get('src')

            if image is None:
                div_style = product.select_one(selector=self.image_selector)['style']
                style = cssutils.parseStyle(div_style)
                url = style['background-image']

                image = url.replace('url(', '').replace(')', '')  # or regex/split/find/slice etc.

            productDict['image'] = image

            if product.select_one(selector=self.link_selector):
                link = product.select_one(selector=self.link_selector).get('href')

                if self.shopName == "SPAR Zimbabwe":
                    domain = urlparse(self.url).netloc

                    # print(domain)

                    link = domain.replace('www.', "https://www.") + link
            else:
                link = ''
            productDict['link'] = link
            # print(product.select_one(selector=self.image_selector))
            productList.append(productDict)
        return productList
        # print(productList)
        # return name, price, image
