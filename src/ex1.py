import errno
import pickle
import glob
import os
import sys

import justext
import requests
from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup
from numpy import mean, std


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


def getMetrics(text):
    res = dict()
    res['lineCount'] = str(text).count('\n')
    res['charCount'] = len(str(text))
    return res


def justextProcess(data):
    outData = dict()
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
                content += str(paragraph.text) if '<p>' in str(
                    paragraph.text) else '<p>{}</p>'.format(str(paragraph.text))
        if content != '':
            out_file = open(
                out_path + os.path.basename(filename),
                mode='w+', encoding='utf-8'
            )
            out_file.write(content)
            out_file.close()
            nWrite += 1
            outData[os.path.basename(filename)] = getMetrics(content)

    print('w#{}/{}'.format(nWrite, nTotal))
    return outData


def boilerpipeProcess(data):
    outData = dict()
    out_path = '../resources/BP/'

    if not os.path.exists(os.path.dirname(out_path)):
        try:
            os.makedirs(os.path.dirname(out_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    nTotal = len(data.keys())
    nWrite = 0

    content = ''
    filenames = list(data.keys())
    for filename in filenames:
        abs_path = os.path.abspath(filename)
        os.rename(abs_path, abs_path + '.html')
        extractor = Extractor(
            extractor='ArticleExtractor',
            url='file://{}.html'.format(abs_path)
        )
        extracted_text = extractor.getText()
        for paragraph in extracted_text.split('\n'):
            content += str(paragraph) if '<p>' in str(
                paragraph) else '<p>{}</p>\n'.format(str(paragraph))
        if content != '':
            out_file = open(
                out_path + os.path.basename(filename),
                mode='w+', encoding='utf-8'
            )
            out_file.write(content)
            out_file.close()
            nWrite += 1
            outData[os.path.basename(filename)] = getMetrics(content)
        os.rename(abs_path + '.html', abs_path)
    print('w#{}/{}'.format(nWrite, nTotal))
    return outData


def computeStastiscalMetrics(metricsRef, metrics):
    res = dict()

    def computeGlobal(metricDict):
        res = dict()
        totalLine = 0
        totalChar = 0
        for filename, metric in metricDict.items():
            totalLine += metric['lineCount']
            totalChar += metric['charCount']
        lineMean = totalLine / len(metricDict.keys())
        charMean = totalChar / len(metricDict.keys())
        lineStd = std(
            list(map(lambda x: x['lineCount'], metricDict.values())))
        charStd = std(
            list(map(lambda x: x['charCount'], metricDict.values())))

        res['totalLine'] = totalLine
        res['totalChar'] = totalChar
        res['lineMean'] = lineMean
        res['charMean'] = charMean
        res['lineStd'] = lineStd
        res['charStd'] = charStd
        return res

    def compare(metricsRef, metric, filename):
        res = dict()
        refMetric = metricsRef[filename.replace('.html', '')]
        res['diffLine'] = abs(refMetric['lineCount'] - metric['lineCount'])
        res['diffChar'] = abs(refMetric['charCount'] - metric['charCount'])
        return res

    ref = computeGlobal(metricsRef)
    if metrics is not None:
        metricsRes = computeGlobal(metrics)
        list_diff = list()
        for filename, metric in metrics.items():
            list_diff.append(compare(metricsRef, metric, filename))
        diffLineMean = mean(list(map(lambda x: x['diffLine'], list_diff)))
        diffCharMean = mean(list(map(lambda x: x['diffChar'], list_diff)))

        diffLineStd = std(list(map(lambda x: x['diffLine'], list_diff)))
        diffCharStd = std(list(map(lambda x: x['diffChar'], list_diff)))

        res['metrics'] = metricsRes
        res['diffLineMean'] = diffLineMean
        res['diffCharMean'] = diffCharMean
        res['diffLineStd'] = diffLineStd
        res['diffCharStd'] = diffCharStd

    res['ref'] = ref
    return res


if __name__ == "__main__":
    path_html = '../resources/Corpus_detourage/html/'
    path_clean = '../resources/Corpus_detourage/clean/'

    htmls = get_files(path_html)
    cleans = get_files(path_clean)

    cleanMetrics = dict()
    for filename, datum in cleans.items():
        cleanMetrics[os.path.basename(filename)] = getMetrics(datum)

    argc = len(sys.argv)
    if argc >= 2:
        if 'jt' in sys.argv[1]:
            pickle.dump(
                justextProcess(htmls),
                open('../resources/tempJT.save', mode='wb+')
            )
        if 'bp' in sys.argv[1]:
            pickle.dump(
                boilerpipeProcess(htmls),
                open('../resources/tempBP.save', mode='wb+')
            )

    try:
        fJT = open('../resources/tempJT.save', mode='rb')
        outMetricsJT = pickle.load(fJT)
        print('JT')
        print(computeStastiscalMetrics(cleanMetrics, outMetricsJT))
        print('##################################################')
    except FileNotFoundError:
        pass
    try:
        fBP = open('../resources/tempBP.save', mode='rb')
        outMetricsBP = pickle.load(fBP)
        print('BP')
        print(computeStastiscalMetrics(cleanMetrics, outMetricsBP))
        print('##################################################')
    except FileNotFoundError:
        pass
