import os
import re
import requests
from bs4 import BeautifulSoup

from .base import BaseConference

VERIFY = True
PROXY = {'https' : 'http://127.0.0.1:7890'}


class CVPR(BaseConference):
    def __init__(self, year, papers_save_path):
        self.year = year
        self.papers_save_path = os.path.join(papers_save_path, f'cvpr{year}')
        self.papers_abstract_path = os.path.join(self.papers_save_path, 'abstract')
        super().__init__()

    def _init_url(self,):
        self.conference_url = f'https://openaccess.thecvf.com/CVPR{self.year}?day=all'
        self.pdf_url_common_part = f'/content/CVPR{self.year}/papers/'
        self.html_url_common_part = f'/content/CVPR{self.year}/html/'
        self.papers_url_prefix = 'https://openaccess.thecvf.com'
        self.papers_pdf_url_prefix = f'https://openaccess.thecvf.com'
        self.papers_html_url_prefix = f'https://openaccess.thecvf.com'
        self.papers_abstract_url_prefix = f'https://openaccess.thecvf.com'

    def get_papers_pdf_url(self):
        response = requests.get(self.conference_url, verify=VERIFY, proxies=PROXY)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = soup.find_all('a', href=re.compile(f"^{re.escape(self.pdf_url_common_part)}"))
            papers_pdf = {}
            for pdf_link in pdf_links:
                paper_pdf_href = pdf_link['href']
                paper_name = self.get_filename_txt(paper_pdf_href)
                papers_pdf[paper_name] = paper_pdf_href
            return papers_pdf
        else:
            print(f'Failed to retrieve the web page. Status code: {response.status_code}. Link: self.conference_url')

    def get_papers_html_url(self):
        response = requests.get(self.conference_url, verify=VERIFY, proxies=PROXY)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            html_links = soup.find_all('a', href=re.compile(f"^{re.escape(self.html_url_common_part)}"))
            papers_html = {}
            for html_link in html_links:
                paper_html_href = html_link['href']
                paper_name = self.get_filename_txt(paper_html_href)
                papers_html[paper_name] = paper_html_href
            return papers_html
        else:
            print(f'Failed to retrieve the web page. Status code: {response.status_code}. Link: self.conference_url')

    def download_paper_abstract(self, paper_abstract_url, paper_abstract_path):
        html_response = requests.get(paper_abstract_url, verify=VERIFY, proxies=PROXY, timeout=(10, 20))
        if html_response.status_code == 200:
            html = html_response.text
            soup = BeautifulSoup(html, 'html.parser')
            abstract = soup.find("div", id='abstract').text
            with open(paper_abstract_path, 'w') as abstract_file:
                abstract_file.write(abstract)
        else:
            print(f'Failed to retrieve the web page. Status code: {html_response.status_code}. Link: {paper_abstract_url}')

    @staticmethod
    def get_filename_txt(filename):
        filename = filename.split('/')[-1]
        filename_componnent = filename.split('_')[1:-3]
        filename_new = " ".join(filename_componnent)
        return filename_new


