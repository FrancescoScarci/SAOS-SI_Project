from bs4 import BeautifulSoup

def clean_content(content):
    soup = BeautifulSoup(content, 'lxml')
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()
