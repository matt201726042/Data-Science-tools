from collections import defaultdict
from gensim import corpora
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim import models
import time

def LDAtrain(docs):
    #common_dictionary = Dictionary(common_texts)
    #common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]
    #return models.ldamulticore.LdaMulticore(corpus=common_corpus, id2word=common_dictionary, num_topics=75), common_dictionary

    # Convert document to tokens
    docs = [doc.split() for doc in docs]

    # A mapping from token to id in each document
    from gensim.corpora import Dictionary
    dictionary = Dictionary(docs)

    # Representing the corpus as a bag of words
    corpus = [dictionary.doc2bow(doc) for doc in docs]

    # Training the model
    return models.ldamulticore.LdaMulticore(corpus=corpus, id2word=dictionary, num_topics=100), dictionary

# data = ["latent Dirichlet allocation (LDA) is a generative statistical model", 
#             "each document is a mixture of a small number of topics",
#             "each document may be viewed as a mixture of various topics"]
# model = LDAtrain(data)

def LDAquery(model, dictionary, test_doc):
    # Some preprocessing for documents like the training the model
    test_doc = [doc.split() for doc in test_doc]
    test_corpus = [dictionary.doc2bow(doc) for doc in test_doc]

    # Method 1
    from gensim.matutils import cossim
    docs = []
    for d in test_corpus:
        docs.append(model.get_document_topics(d, minimum_probability=0))
    return [(cossim(docs[0], docs[i]) + 1) / 2 for i in range(1,len(docs))][0]
    #doc1 = model.get_document_topics(test_corpus[0], minimum_probability=0)
    #doc2 = model.get_document_topics(test_corpus[1], minimum_probability=0)
    #return (cossim(doc1, doc2) + 1) / 2

# LDAquery(model, ["abc", "fsdgdg"])