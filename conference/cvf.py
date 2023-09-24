import os
import re
import requests
from bs4 import BeautifulSoup

PROXY = {'https' : 'http://127.0.0.1:7890'}
VERIFY = True

class CVFConference():
    def __init__(self, conference, conference_path):
        self.conference = conference
        self.conference_path = conference_path
        self.papers_abstract_path = os.path.join(conference_path, 'abstract')
        self.conference_url = f'https://openaccess.thecvf.com/{conference}?day=all'
        self.common_param = f'/content/{conference}/papers/'
        self.pdf_url_common_param = f'/content/{conference}/papers/'
        self.html_url_common_param = f'/content/{conference}/html/'
        self.pdf_url_prefix = f'https://openaccess.thecvf.com/content/{conference}/papers/'
        self.html_url_prefix = f'https://openaccess.thecvf.com/content/{conference}/html/'
        self.papers_url_prefix = 'https://openaccess.thecvf.com'
        self._init_conference()
    
    def _init_conference(self,):
        if not os.path.exists(self.conference_path):
            os.makedirs(self.conference_path)
        if not os.path.exists(self.papers_abstract_path):
            os.makedirs(self.papers_abstract_path)

    def get_papers_name(self,):
        response = requests.get(self.conference_url, verify=VERIFY, proxies=PROXY)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = soup.find_all('a', href=re.compile(f"^{re.escape(self.pdf_url_common_param)}"))
            papers_name_list = []
            for i in range(len(pdf_links)):
                pdf_link = pdf_links[i]
                pdf_href = pdf_link['href']
                pdf_name = pdf_href.split('/')[-1]
                paper_name = pdf_name[:-4]
                papers_name_list.append(paper_name)
            return sorted(papers_name_list)
        else:
            print(f'Failed to retrieve the web page. Status code: {response.status_code}')

    def get_papers_pdf_url(self,):
        response = requests.get(self.conference_url, verify=VERIFY, proxies=PROXY)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = soup.find_all('a', href=re.compile(f"^{re.escape(self.pdf_url_common_param)}"))
            papers_pdf_list = []
            for pdf_link in pdf_links:
                papers_pdf_list.append(pdf_link['href'])
            return sorted(papers_pdf_list)
        else:
            print(f'Failed to retrieve the web page. Status code: {response.status_code}')

    def get_papers_html_url(self,):
        response = requests.get(self.conference_url, verify=VERIFY, proxies=PROXY)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            html_links = soup.find_all('a', href=re.compile(f"^{re.escape(self.html_url_common_param)}"))
            papers_html_list = []
            for html_link in html_links:
                papers_html_list.append(html_link['href'])
            return sorted(papers_html_list)
        else:
            print(f'Failed to retrieve the web page. Status code: {response.status_code}')

    def downlaod_papers_abstract(self, papers_html_url_list):
        for paper_html_url in papers_html_url_list:
            paper_name = paper_html_url.split('/')[-1]
            paper_name = paper_name[:-5]
            paper_abstract_path = os.path.join(self.papers_abstract_path, paper_name+'.txt')
            if not os.path.exists(paper_abstract_path):
                paper_abstract_url = self.papers_url_prefix + paper_html_url
                self.download_paper_abstract(paper_abstract_url, paper_abstract_path)

    def download_paper_abstract(self, paper_abstract_url, paper_abstract_path):
        html_response = requests.get(paper_abstract_url, verify=VERIFY, proxies=PROXY, timeout=(10, 20))
        if html_response.status_code == 200:
            html = html_response.text
            soup = BeautifulSoup(html, 'html.parser')
            abstract = soup.find("div", id='abstract').text
            with open(paper_abstract_path, 'w') as abstract_file:
                abstract_file.write(abstract)
        else:
            print(f'Failed to retrieve the web page. Status code: {html_response.status_code}')

    def get_papers_abstract(self,):
        papers_abstract_txt = os.listdir(self.papers_abstract_path)
        papers_html_url_list = self.get_papers_html_url()
        if not len(papers_abstract_txt) == len(papers_html_url_list):
            self.downlaod_papers_abstract(papers_html_url_list)
        papers_abstract = {}
        for paper_abstract_txt in papers_abstract_txt:
            paper_abstract_path = os.path.join(self.papers_abstract_path ,paper_abstract_txt)
            with open(paper_abstract_path) as paper_abstract_file:
                abstract_data = paper_abstract_file.read()
            papers_abstract[paper_abstract_txt[:-4]] = abstract_data
        return papers_abstract

    def downlaod_papers(self, papers_name, save_path):
        for paper_name in papers_name:
            paper_url = self.pdf_url_prefix + paper_name + '.pdf'
            response_pdf = requests.get(paper_url, verify=VERIFY, proxies=PROXY, timeout=(10, 20))
            if response_pdf.status_code == 200:
                filename = paper_url.split('/')[-1]
                filename = CVFConference.format_filename(filename)
                filename = os.path.join(save_path, filename)
                CVFConference.download_pdf(response_pdf, filename)
            else:
                print('PDF file download failed, ', response_pdf.status_code)
        return len(papers_name)

    def filter_papers(self, papers, include_keywords_list, exclude_keywords_list=None):
        papers_include = {}
        for paper_name in papers:
            for include_keywords in include_keywords_list:
                paper_abstract = papers[paper_name]
                if CVFConference.filter_parallel(paper_abstract, include_keywords, 'include'):
                    papers_include[paper_name] = paper_abstract
                    continue
        if exclude_keywords_list:
            papers_exclude = {}
            for paper_name in papers_include:
                for exclude_keywords in exclude_keywords_list:
                    paper_abstract = papers[paper_name]
                    if CVFConference.filter_parallel(paper_abstract, exclude_keywords, 'exclude'):
                        papers_exclude[paper_name] = paper_abstract
                        continue
        else:
            papers_exclude = papers_include
        papers_selected = list(papers_exclude.keys())
        return papers_selected

    def analyse_conference(self, task, include_keywords, exclude_keywords):
        task_path = os.path.join(self.conference_path, task)
        if not os.path.exists(task_path):
            os.makedirs(task_path)
        papers_abstract = self.get_papers_abstract()
        result = self.filter_papers(papers_abstract, include_keywords, exclude_keywords)
        total_download_papers = self.downlaod_papers(result, task_path)
        print(f'successfully !!! Totally Find {total_download_papers} papers !!!')
    
    @staticmethod
    def download_pdf(response_pdf, filename):
        if os.path.exists(filename):
            print(f'PDF file is exist: "{os.path.split(filename)[-1]}".')
        else:
            with open(filename, 'wb') as pdf_file:
                pdf_file.write(response_pdf.content)
            print(f'PDF file download successfully: "{os.path.split(filename)[-1]}".')

    @staticmethod
    def format_filename(filename):
        filename_componnent = filename.split('_')[1:-3]
        filename_new = " ".join(filename_componnent)
        filename_new = filename_new + '.pdf'
        return filename_new
    
    @staticmethod
    def filter_parallel(content, keywords, mode='include'):
        assert mode in ['include', 'exclude']
        if not (type(keywords) is tuple):
            keywords = (keywords,)
        num = 0
        for keyword in keywords:
            keyword = re.compile(re.escape(keyword), re.IGNORECASE)
            if keyword.search(content):
                num += 1
            else:
                num += 0
        if mode == 'include':
            if len(keywords) == num:
                return True
            else:
                return False
        if mode == 'exclude':
            if num == 0:
                return True
            else:
                return False

