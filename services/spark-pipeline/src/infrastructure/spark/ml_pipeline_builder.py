from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, IndexToString, Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.classification import NaiveBayes
from typing import List


def build_multilingual_stop_words() -> List[str]:
    english: List[str] = StopWordsRemover.loadDefaultStopWords("english")
    spanish: List[str] = StopWordsRemover.loadDefaultStopWords("spanish")
    return list(set(english + spanish))


def build_sentiment_pipeline(label_col: str = "sentimiento") -> Pipeline:
    label_indexer = StringIndexer(
        inputCol=label_col,
        outputCol="label_idx",
        handleInvalid="skip"
    )

    tokenizer = Tokenizer(
        inputCol="text_clean",
        outputCol="tokens"
    )

    stop_words: List[str] = build_multilingual_stop_words()
    stop_words_remover = StopWordsRemover(
        inputCol="tokens",
        outputCol="tokens_clean",
        stopWords=stop_words
    )

    hashing_tf = HashingTF(
        numFeatures=2 ** 14,
        inputCol="tokens_clean",
        outputCol="tf"
    )

    idf = IDF(
        inputCol="tf",
        outputCol="features"
    )

    nb = NaiveBayes(
        labelCol="label_idx",
        featuresCol="features",
        smoothing=1.0
    )

    label_converter = IndexToString(
        inputCol="prediction",
        outputCol="predicted_label"
    )

    return Pipeline(stages=[
        label_indexer,
        tokenizer,
        stop_words_remover,
        hashing_tf,
        idf,
        nb,
        label_converter
    ])
