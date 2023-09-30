import os
import re
import requests
from bs4 import BeautifulSoup


from .base import BaseConference
from .tools import format_filename

VERIFY = True
PROXY = {'https' : 'http://127.0.0.1:7890'}


class NeurIPS(BaseConference):
    def __init__(self, year, papers_save_path):
        self.year = year
        self.papers_save_path = os.path.join(papers_save_path, f'neurips{year}')
        self.papers_abstract_path = os.path.join(self.papers_save_path, 'abstract')
        super().__init__()

    def _init_url(self,):
        self.conference_url = f'https://neurips.cc/virtual/{self.year}/papers.html?filter=titles'
        self.html_url_common_part = f'/virtual/{self.year}/poster/'
        self.pdf_home_url_common_part = 'https://proceedings.neurips.cc/paper_files/paper/'
        self.pdf_url_common_part = f'/paper_files/paper/{self.year}/file'
        self.papers_pdf_url_prefix = 'https://proceedings.neurips.cc'
        self.papers_html_url_prefix = 'https://neurips.cc'
        self.papers_abstract_url_prefix = 'https://neurips.cc'

    def get_paper_pdf_url(self, paper_home_url):
        paper_home_response = requests.get(paper_home_url, verify=VERIFY, proxies=PROXY)
        if paper_home_response.status_code == 200:
            soup = BeautifulSoup(paper_home_response.text, 'html.parser')
            paper_pdf_home_link = soup.find('a', href=re.compile(f"^{re.escape(self.pdf_home_url_common_part)}"), title='Paper')
            paper_pdf_home_url = paper_pdf_home_link['href']
        else:
            print(f'Failed to retrieve the web page. Status code: {paper_home_response.status_code}. Link: {paper_home_url}')
        
        paper_pdf_home_response = requests.get(paper_pdf_home_url, verify=VERIFY, proxies=PROXY)
        if paper_pdf_home_response.status_code == 200:
            paper_pdf_soup = BeautifulSoup(paper_pdf_home_response.text, 'html.parser')
            paper_pdf_link = paper_pdf_soup.find('a', href=re.compile(f"^{re.escape(self.pdf_url_common_part)}"), text='Paper')
            paper_pdf_url = paper_pdf_link['href']
        else:
            print(f'Failed to retrieve the web page. Status code: {paper_pdf_home_response.status_code}. Link: {paper_pdf_home_url}')
        return paper_pdf_url

    def get_papers_pdf_home_url(self, papers_html_url_suffix=None):
        papers_pdf_url = {}
        if papers_html_url_suffix == None:
            papers_html_url_suffix = self.get_papers_html_url()
        for paper_name in papers_html_url_suffix:
            paper_html_url = self.papers_html_url_prefix + papers_html_url_suffix[paper_name]
            paper_home_response = requests.get(paper_html_url, verify=VERIFY, proxies=PROXY)
            if paper_home_response.status_code == 200:
                soup = BeautifulSoup(paper_home_response.text, 'html.parser')
                paper_pdf_link = soup.find('a', href=re.compile(f"^{re.escape(self.pdf_home_url_common_part)}"), title='Paper')
                papers_pdf_url[paper_name] = paper_pdf_link['href']
            else:
                print(f'Failed to retrieve the web page. Status code: {paper_home_response.status_code}. Link: {paper_html_url}')
        return papers_pdf_url

    def get_papers_pdf_url(self, papers_html_url_suffix=None):
        papers_pdf_url = {}
        if papers_html_url_suffix == None:
            papers_html_url_suffix = self.get_papers_html_url()
        for paper_name in papers_html_url_suffix:
            paper_html_url = self.papers_html_url_prefix + papers_html_url_suffix[paper_name]
            paper_home_response = requests.get(paper_html_url, verify=VERIFY, proxies=PROXY)
            if paper_home_response.status_code == 200:
                soup = BeautifulSoup(paper_home_response.text, 'html.parser')
                paper_pdf_link = soup.find('a', href=re.compile(f"^{re.escape(self.pdf_home_url_common_part)}"), title='Paper')
                papers_pdf_url[paper_name] = paper_pdf_link['href']
        return papers_pdf_url
    
    def get_papers_pdf_url_selected(self, papers_name_selected):
        papers_home_url = self.get_papers_html_url()
        papers_pdf_url_selected = {}
        for paper_name in papers_name_selected:
            paper_home_url_suffix = papers_home_url[paper_name]
            paper_home_url = self.papers_html_url_prefix + paper_home_url_suffix
            paper_pdf_url = self.get_paper_pdf_url(paper_home_url)
            papers_pdf_url_selected[paper_name] = paper_pdf_url
        return papers_pdf_url_selected

    def get_papers_html_url(self, ):
        papers_html = {}
        html_response = requests.get(self.conference_url, verify=VERIFY, proxies=PROXY)
        if html_response.status_code == 200:
            soup = BeautifulSoup(html_response.text, 'html.parser')
            li_elements = soup.find_all('li')
            for li_element in li_elements:
                a_element = li_element.find('a', href=re.compile(f"^{re.escape(self.html_url_common_part)}"))
                if a_element:
                    paper_html = a_element['href']
                    paper_name = a_element.get_text()
                    paper_name = format_filename(paper_name)
                    papers_html[paper_name] = paper_html
        return papers_html

    def download_paper_abstract(self, paper_abstract_url, paper_abstract_path):
        html_response = requests.get(paper_abstract_url, verify=VERIFY, proxies=PROXY)
        if html_response.status_code == 200:
            soup = BeautifulSoup(html_response.text, 'html.parser')
            abstract = soup.find('div', id='abstractExample')
            abstract = abstract.get_text()
            with open(paper_abstract_path, 'w') as abstract_file:
                abstract_file.write(abstract)
        else:
            print(f'Failed to retrieve the web page. Status code: {html_response.status_code}. Link: {paper_abstract_url}')
