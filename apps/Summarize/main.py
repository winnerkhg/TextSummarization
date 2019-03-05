import sys
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import operator
from django.core.files.storage import default_storage

factory = StemmerFactory()
stemmer = factory.create_stemmer()

#fungsi untuk memuat stopwords
def load_stopWords():
	f = open('apps/Summarize/stopword.txt','r+');
	return f.readlines()

#pemanggilan fungsi load_stopwords()
stopwords = load_stopWords()

#fungsi untuk praprocessing data yaitu fungsi cleanData
def cleanData(kalimat):
    # sentence = re.sub('[^A-Za-z0-9 ]+', '', sentence)
    # sentence filter(None, re.split("[.!?", setence))
    ret = [] #pembuatan array bernama ret
    kalimat += stemmer.stem(kalimat) #dilakukan stemming kalimat
    for kata in kalimat.split(): #looping untuk setiap kata dalam kalimat tersebut, apakah ada di stopword atau tidak.
        if not kata in stopwords:
            ret.append(kata)#simpan kata yang tidak ada distopword pada array ret
    return " ".join(ret) #kembalikan kata pada array ret


#fungsi getVectorSpace utk menciptakan array vocab
def getVectorSpace(cleanSet):
    vocab = {}
    for data in cleanSet:
        for kata in data.split():
            vocab[data] = 0
    return vocab.keys() #kembalikan array vocab


#fungsi untuk menghitung nilai Similaritas dengan menggunakan teknik Cosine Similarity
def calculateSimilarity(kalimat, dok): #parameternya ialah kalimat dan dokumen
    if dok == []:
        return 0
    vocab = {} #array vocab dari getVectorSpace

    #looping setiap kata pada kalimat
    for kata in kalimat:
        vocab[kata] = 0
    docInOneSentence = '';

    #looping setiap kalimat pada dokumen
    for t in dok:
        docInOneSentence += (t + ' ')
        for kata in t.split():
            vocab[kata] = 0
    #inisialisasi variabel cv sebagai CountVectorizer
    cv = CountVectorizer(vocabulary=vocab.keys())
    vektorDok = cv.fit_transform([docInOneSentence])
    vektorKalimat = cv.fit_transform([kalimat])
    return cosine_similarity(vektorDok, vektorKalimat)[0][0]

#fungsi unggah teks yang akan diringkas
def main(teks):
    #inisialisasi dokumen input dengan nama variabel data
    data = default_storage.open(teks, 'r')

    #dokumen yang diunggah dibaca per kalimat
    texts = data.readlines()

    #tutup data
    data.close()

    kalimat = []
    clean = []
    kalimatOriginal = {}
    import time
    start = time.time()

    # pemanggilan data cleaning
    for line in texts:
        #split data setiap ditemui simbol '.'
        parts = line.split('.')
        for part in parts:
            cl = cleanData(part)
            # print cl
            kalimat.append(part)
            clean.append(cl)
            kalimatOriginal[cl] = part
    setClean = set(clean)

    # calculate Similarity score each sentence with whole documents
    #menghitung nilai Similaritas dari masing-masing sentence dengan keseltuhan dokumen
    scores = {}
    for data in clean:
        temp_doc = setClean - set([data])
        score = calculateSimilarity(data, list(temp_doc))
        scores[data] = score
    # print score

    # Menghitung nilai MMR
    n = 20 * len(kalimat) / 100

    #nilai alpha = 0.7
    alpha = 0.7

    summarySet = []
    while n > 0:
        mmr = {}
        # kurangkan dengan set summary
        for sentence in scores.keys():
            if not sentence in summarySet:
                mmr[sentence] = alpha * scores[sentence] - (1 - alpha) * calculateSimilarity(sentence, summarySet)
        selected = max(mmr.items(), key=operator.itemgetter(1))[0]
        summarySet.append(selected)
        n -= 1

    # rint str(time.time() - start)
    summarize = ''
    tx = ''
    print('\nSummary:\n')
    for sentence in summarySet:
        summarize+=(kalimatOriginal[sentence].lstrip(' '))+'.'
        tx+=sentence
    from rouge import Rouge
    summary = summarize
    reference = tx
    rouge = Rouge()
    accuracy = rouge.get_scores(summary, reference)
    return summarize,clean, accuracy

def ketik(teks):
    data = default_storage.open(teks,'r')
    texts = data.readlines()
    data.close()
    kalimat = []
    clean = []
    kalimatOriginal = {}
    import time
    start = time.time()
    # Data cleansing
    for line in texts:
        parts = line.split('.')
        for part in parts:
            cl = cleanData(part)
            # print cl
            kalimat.append(part)
            clean.append(cl)
            kalimatOriginal[cl] = part
    setClean = set(clean)
    # calculate Similarity score each sentence with whole documents
    scores = {}
    for data in clean:
        temp_doc = setClean - set([data])
        score = calculateSimilarity(data, list(temp_doc))
        scores[data] = score
    # print score

    # calculate MMR
    n = 20 * len(kalimat) / 100
    alpha = 0.7
    summarySet = []
    while n > 0:
        mmr = {}
        # kurangkan dengan set summary
        for sentence in scores.keys():
            if not sentence in summarySet:
                mmr[sentence] = alpha * scores[sentence] - (1 - alpha) * calculateSimilarity(sentence, summarySet)
        selected = max(mmr.items(), key=operator.itemgetter(1))[0]
        summarySet.append(selected)
        n -= 1

    # rint str(time.time() - start)
    summarize =''
    tx =""
    print('\nSummary:\n')
    for sentence in summarySet:
        summarize+=(kalimatOriginal[sentence].lstrip(' '))+'.'
        tx+=sentence
    from rouge import Rouge
    summary = summarize
    reference = tx
    rouge = Rouge()
    accuracy = rouge.get_scores(summary, reference)
    return summarize, clean, accuracy