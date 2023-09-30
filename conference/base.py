import os
import requests
from abc import ABCMeta,abstractmethod

from .tools import filter_parallel, format_filename, download_pdf

VERIFY = True
PROXY = {'https' : 'http://127.0.0.1:7890'}

class BaseConference(metaclass=ABCMeta):
    def __init__(self,):
        self._init_url()
        self._init_conference()
    
    @abstractmethod
    def _init_url(self,):
        self.conference_url = None
        self.papers_pdf_url_prefix = None
        self.papers_html_url_prefix = None
        self.papers_abstract_url_prefix = None

    def _init_conference(self,):
        if not os.path.exists(self.papers_save_path):
            os.makedirs(self.papers_save_path)
        if not os.path.exists(self.papers_abstract_path):
            os.makedirs(self.papers_abstract_path)

    def get_papers_name(self,):
        """
        Get the papers name list.

        Return:
            A list that contain all papers name.
        """
        pass

    @abstractmethod
    def get_papers_pdf_url(self,):
        """
        Get the papers pdf url dict.
        Return:
            A dict that contain all papers pdf url, where keys index papers
            name and values index paper pdf url.
        """
        pass

    def get_paper_pdf_url(self,):
        """
        Get the paper pdf url.

        """
        pass

    @abstractmethod
    def get_papers_html_url(self,):
        """
        Get the papers home html url dict.

        Return:
            A dict that contain all papers home html url, where keys index papers
            name and values index paper home html url.
        """
        pass

    def get_papers_abstract(self,):
        papers_abstract_txt_filename = os.listdir(self.papers_abstract_path)
        papers_html_url_list = self.get_papers_html_url()
        # download papers abstract
        if not len(papers_abstract_txt_filename) == len(papers_html_url_list):
            self.download_papers_abstract(papers_html_url_list)
        # load papers abstract from txt file
        papers_abstract = {}
        for paper_abstract_txt_filename in papers_abstract_txt_filename:
            paper_abstract_path = os.path.join(self.papers_abstract_path ,paper_abstract_txt_filename)
            with open(paper_abstract_path) as paper_abstract_file:
                abstract_data = paper_abstract_file.read()
            papers_abstract[paper_abstract_txt_filename[:-4]] = abstract_data
        return papers_abstract

    def get_papers_pdf_url_selected(self, papers_name_selected):
        papers_pdf_url = self.get_papers_pdf_url()
        papers_pdf_url_selected = {}
        for paper_name_selected in papers_name_selected:
            papers_pdf_url_selected[paper_name_selected] = papers_pdf_url[paper_name_selected]
        return papers_pdf_url_selected

    def download_papers_abstract(self, papers_abstract_url_total:dict):
        for paper_name in papers_abstract_url_total:
            paper_abstract_url_suffix = papers_abstract_url_total[paper_name]
            paper_name_file = format_filename(paper_name)
            paper_abstract_path = os.path.join(self.papers_abstract_path, paper_name_file+'.txt')
            if not os.path.exists(paper_abstract_path):
                paper_abstract_url = self.papers_abstract_url_prefix + paper_abstract_url_suffix
                self.download_paper_abstract(paper_abstract_url, paper_abstract_path)

    @abstractmethod
    def download_paper_abstract(self, paper_abstract_url, paper_abstract_path):
        """
        Abstract:
            Download the paper abstract from website to the txt file.
        Input:
            paper_abstract_url: paper home html url
            paper_abstract_path: a txt file path saving the abstract of the paper
        """
        pass

    def filter_papers(self, papers_abstract_total, include_keywords_list, exclude_keywords_list=None):
        papers_include = {}
        # select the papers that contain the given keywords from include_keywords
        for paper_name in papers_abstract_total:
            for include_keywords in include_keywords_list:
                paper_abstract = papers_abstract_total[paper_name]
                if filter_parallel(paper_abstract, include_keywords):
                    papers_include[paper_name] = paper_abstract
                    
        papers_exclude = papers_include.copy()
        # exclude the papers that contain the given keywords from exclude_keywords
        if exclude_keywords_list:
            for paper_name in papers_include:
                for exclude_keywords in exclude_keywords_list:
                    paper_abstract = papers_abstract_total[paper_name]
                    if filter_parallel(paper_abstract, exclude_keywords):
                        del papers_exclude[paper_name]
                        break
        papers_selected = list(papers_exclude.keys())
        return papers_selected

    def download_papers(self, papers_pdf_url_suffix: dict, save_path: str):
        """
        Abstract:
            Download papers.

        Input:
            papers_pdf_url_list: A dict, where keys index papers name and values index papers pdf url suffix.
            save_path: download the papers to this path.
        """
        for paper_name in papers_pdf_url_suffix:
            paper_url = self.papers_pdf_url_prefix + papers_pdf_url_suffix[paper_name]
            response_pdf = requests.get(paper_url, verify=VERIFY, proxies=PROXY, timeout=(10, 20))
            if response_pdf.status_code == 200:
                filename = paper_name + '.pdf'
                filename = os.path.join(save_path, filename)
                download_pdf(response_pdf, filename)
            else:
                print(f'PDF file download failed. Status code: {response_pdf.status_code}, Link: {paper_url}')
        return len(papers_pdf_url_suffix)

    def analyse_conference(self, task, include_keywords, exclude_keywords):
        # initialization for task
        task_path = os.path.join(self.papers_save_path, task)
        if not os.path.exists(task_path):
            os.makedirs(task_path)
        # get papers abstract
        papers_abstract_total = self.get_papers_abstract()
        # filter papers based on abstract
        papers_name_selected = self.filter_papers(papers_abstract_total, include_keywords, exclude_keywords)
        # download the filtered papers
        papers_pdf_url_selected = self.get_papers_pdf_url_selected(papers_name_selected)
        # download all the paper pdf
        total_download_papers = self.download_papers(papers_pdf_url_selected, task_path)

        print(f'successfully !!!    Totally Find {total_download_papers} papers !!!')

