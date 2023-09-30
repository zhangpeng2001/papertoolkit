import re
import os


def filter_parallel(content, keywords):
    """
    Filter the content to determinate whether it contain all the 
    words from the given keywords.
    Input:
        content: a string.
        keywords: a tuple or a string.
    Return:
        True: if the content contain all words from the keywords.
        False: if the content not contain all words from the keywords.
    """
    if not (type(keywords) is tuple):
        keywords = (keywords,)
    num = 0
    for keyword in keywords:
        keyword = re.compile(re.escape(keyword), re.IGNORECASE)
        if keyword.search(content):
            num += 1
        else:
            num += 0
    if len(keywords) == num:
        return True
    else:
        return False



def download_pdf(response_pdf, filename):
    if os.path.exists(filename):
        print(f'PDF file is exist: "{os.path.split(filename)[-1]}".')
    else:
        with open(filename, 'wb') as pdf_file:
            pdf_file.write(response_pdf.content)
        print(f'PDF file download successfully: "{os.path.split(filename)[-1]}".')



def format_filename(filename):
    filename_trans_table = str.maketrans({':':'', '?':'', '$':'', '/':'', '\\':'', '"':'', '*':''})
    filename = filename.translate(filename_trans_table)
    return filename


