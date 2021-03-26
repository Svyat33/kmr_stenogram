import base64
import logging

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class Document(BaseModel):
    title: str
    link: str
    file_content: str
    file_name: str


logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)


# logger.setLevel(logging.DEBUG)


class LoadDocuments:
    def __init__(self, count: int = 10):
        self.current_page = 0
        self.count = count
        self.__reset()

    def __reset(self):
        logger.debug("Reset iterator")
        self.__session = requests.session()
        self.__page = None

    def current_link(self) -> str:
        lnk = f"https://kmr.gov.ua/uk/stenogramu?" \
              f"title=&field_start_date_n_h_value%5Bmin%5D&" \
              f"field_start_date_n_h_value%5Bmax%5D&" \
              f"page={self.current_page}"
        logger.debug("Get current link\n %s", lnk)
        return lnk

    def __docs_from_page(self) -> Document:
        '''Генератор отдающий все документы на странице'''
        span_list = [span
                     for span in self.__page.find_all('span',
                                                      class_='field-content')
                     if span.find('a') and 'href' in span.find('a').attrs]
        for span in span_list:
            a = span.find('a')
            document_link = a.attrs.get('href')
            if document_link.find('.odt') < 0:
                continue
            doc: requests.Response = self.__session.get(document_link)
            if doc.ok:
                yield Document.parse_obj({
                    'title': a.text,
                    'link': document_link,
                    'file_name': document_link.rsplit("/")[-1],
                    'file_content': base64.b64encode(doc.content).decode(),
                })

        if self.__page.select_one('a:-soup-contains("наступна")'):
            self.current_page += 1
        else:
            logger.debug("Больше некуда листать. Останавливаемся.")
            self.current_page = -1
        self.__page = None

    def __iter__(self):
        logger.debug("Start iterator")
        self.__reset()
        self.__load_page()
        return self

    def __load_page(self):
        if self.__page is None:
            logger.debug("Page not loaded. Get it!")
            ret = self.__session.get(self.current_link())
            if not ret.ok:
                raise ConnectionError("Page unavailable")
            self.__page = BeautifulSoup(ret.content, 'lxml')
            logger.debug("Страница скачана создаю генератор")
            self.__generator = self.__docs_from_page()

    def __next__(self) -> Document:
        if self.count <= 0 or self.current_page < 0:
            raise StopIteration
        self.count -= 1
        self.__load_page()
        try:
            return next(self.__generator)
        except StopIteration:
            return self.__next__()
