from collections import defaultdict
from gensim import corpora
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim import models

def LDAtrain(docs):
    # Convert document to tokens
    docs = [doc.split() for doc in docs]

    # A mapping from token to id in each document
    from gensim.corpora import Dictionary
    dictionary = Dictionary(docs)

    # Representing the corpus as a bag of words
    corpus = [dictionary.doc2bow(doc) for doc in docs]

    # Training the model
    return models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=50), dictionary

#data = ["latent Dirichlet allocation (LDA) is a generative statistical model", 
#            "each document is a mixture of a small number of topics",
#            "each document may be viewed as a mixture of various topics"]
#model, dictionary = LDAtrain(data)

def LDAquery(model, dictionary, a, b):
    a.extend([b])
    test_doc = a
    # Some preprocessing for documents like the training the model
    test_doc = [doc.split() for doc in test_doc]
    test_corpus = [dictionary.doc2bow(doc) for doc in test_doc]

    # Method 1
    from gensim.matutils import cossim
    docs = [model.get_document_topics(tC, minimum_probability=0) for tC in test_corpus]
    return [cossim(docs[0], docs[i]) for i in range(len(docs))]

#LDAquery(model, dictionary, ["document gay"], "various topics")