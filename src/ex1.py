import os
import glob

import justext
import requests
from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup


def get_files(path):
    texts = dict()
    nOpened = 0
    nTotal = 0

    for filename in glob.glob(os.path.join(path, u'*')):
        file = open(filename, encoding='utf-8', mode='r')
        nTotal += 1
        try:
            texts[filename] = file.read()
            nOpened += 1
        except UnicodeDecodeError:
            pass
        file.close()

    print('o#{}/{}'.format(nOpened, nTotal))
    return texts


def justextProcess(data):
    out_path = '../resources/JT/'

    if not os.path.exists(os.path.dirname(out_path)):
        try:
            os.makedirs(os.path.dirname(out_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    nTotal = len(data.keys())
    nWrite = 0

    for filename, datum in data.items():
        content = ''
        paragraphs = justext.justext(
            datum, justext.get_stoplist('English')
        )
        for paragraph in paragraphs:
            if not paragraph.is_boilerplate:
                content += str(paragraph.text) if str(paragraph.text).find(
                    '<p>') else '<p>{}</p>'.format(str(paragraph.text))
        if content != '':
            out_file = open(
                out_path + os.path.basename(filename),
                mode='w+', encoding='utf-8'
            )
            out_file.write(content)
            out_file.close()
            nWrite += 1

    print('w#{}/{}'.format(nWrite, nTotal))


if __name__ == "__main__":
    path_html = '../resources/Corpus_detourage/html/'
    path_clean = '../resources/Corpus_detourage/clean/'

    htmls = get_files(path_html)
    cleans = get_files(path_clean)

    justextProcess(htmls)
