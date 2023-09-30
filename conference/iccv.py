import os

from .cvpr import  CVPR


class ICCV(CVPR):
    def __init__(self, year, papers_save_path):
        self.year = year
        self.papers_save_path = os.path.join(papers_save_path, f'iccv{year}')
        self.papers_abstract_path = os.path.join(self.papers_save_path, 'abstract')
        self._init_url()
        self._init_conference()

    def _init_url(self):
        self.conference_url = f'https://openaccess.thecvf.com/ICCV{self.year}?day=all'
        self.pdf_url_common_part = f'/content/ICCV{self.year}/papers/'
        self.html_url_common_part = f'/content/ICCV{self.year}/html/'
        self.papers_url_prefix = 'https://openaccess.thecvf.com'
        self.papers_pdf_url_prefix = f'https://openaccess.thecvf.com'
        self.papers_html_url_prefix = f'https://openaccess.thecvf.com'

