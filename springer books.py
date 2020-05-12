import PyPDF2
import re
from bs4 import BeautifulSoup
import requests
import os


def read_pdf(pdf_name, base_url):
    pdf_reader = PyPDF2.PdfFileReader(pdf_name)
    max_page = pdf_reader.numPages
    urls = []
    for pageNum in range(0, max_page):
        page_text = pdf_reader.getPage(pageNum).extractText()
        find = re.findall(base_url, page_text)
        urls += find
    return urls


def get_response(url):
    response = requests.get(url)
    return response.text


def found(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


if __name__ == '__main__':
    base_reg_ex = re.compile("http://link.springer.com/openurl\?genre=book&isbn=[0-9]*-[0-9]*-[0-9]*-[0-9]*-[0-9]*")
    urls = read_pdf("Springer Ebooks.pdf", base_reg_ex)
    print(urls)
    print(len(urls))
    base_download_url = 'https://link.springer.com{}'
    if not os.path.exists('Books'):
        os.mkdir('Books')  # Create a new folder to store the Books
    for url in urls:
        data = get_response(url)
        soup = BeautifulSoup(data, features='html.parser')   # Create a BeautifulSoup instance
        downloads = soup.find_all('div', {'class': 'cta-button-container__item'})
        titles = soup.find_all('div', {'class': 'page-title'})
        book_title = titles[0].find('h1').text
        if found(book_title+'.pdf', 'Books'):
            print("{} Found".format(book_title))
            continue
        if downloads:   # If the 'download PDF' button is available
            download_url = base_download_url.format(downloads[0].find('a').get('href'))
            print(download_url, book_title)

            # Download the book

            r = requests.get(download_url, allow_redirects=True)
            open('Books/{}.pdf'.format(book_title), 'wb').write(r.content)
