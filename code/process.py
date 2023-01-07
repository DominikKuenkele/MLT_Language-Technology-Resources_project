import copy
import datetime
import pickle
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pprint import pprint

from loader import ParagraphLoader, ParagraphSample


@dataclass(kw_only=True, slots=True)
class Post:
    post_id: str
    date: datetime
    author_id: str

    def __hash__(self) -> int:
        return hash((self.post_id))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Post):
            return self.post_id == __o.post_id
        return False


@dataclass
class AuthorData:
    sentiment: float = -1
    bigram_distribution: dict = field(default_factory=dict)
    paragraphs: list[ParagraphSample] = field(default_factory=list)


if __name__ == '__main__':
    with open('saved_posts.pickle', 'rb') as f:
        saved_posts: list[Post] = pickle.load(f)

    post_dict = {post.post_id: post.author_id for post in saved_posts}

    authors = defaultdict(AuthorData)
    paragrapgh_loader = ParagraphLoader('data/swe-absa-bank-imm/P_annotation.tsv')
    for sample in paragrapgh_loader.samples:
        if sample.document_id in post_dict:
            author_id = post_dict[sample.document_id]
            authors[author_id].paragraphs.append(copy.deepcopy(sample))

    print(len(authors), len(saved_posts))

    sorted_authors = sorted(authors.items(), key=lambda x: len(x[1].paragraphs), reverse=True)
    more_than_one_post = [author for author in sorted_authors if len(
        {paragraph.paragraph_id for paragraph in author[1].paragraphs}) > 1]
    more_than_two_post = [author for author in sorted_authors if len(
        {paragraph.paragraph_id for paragraph in author[1].paragraphs}) > 2]

    number_of_one_posts = sum(
        len({paragraph.paragraph_id for paragraph in author[1].paragraphs}) for author in more_than_one_post)
    number_of_two_posts = sum(
        len({paragraph.paragraph_id for paragraph in author[1].paragraphs}) for author in more_than_two_post)

    print(len(more_than_one_post), number_of_one_posts)
    print(len(more_than_two_post), number_of_two_posts)

    for author, author_data in authors.items():
        author_data.sentiment = sum(paragraph.average
                                    for paragraph in set(author_data.paragraphs)) / len(set(author_data.paragraphs))

    sentiments = {author_id: author_data.sentiment for author_id, author_data in authors.items()}
    sorted_sentiments = sorted(sentiments.items(), key=lambda x: x[1])

    # bigram_model
    number_words = 0
    unigram_vocab = Counter()
    bigram_vocab = Counter()
    for author_data in authors.values():
        for paragraph in author_data.paragraphs:
            unigram_vocab.update(paragraph.tokenized_text)
            bigram_vocab.update(zip(paragraph.tokenized_text[:-1], paragraph.tokenized_text[1:]))
            number_words += len(paragraph.tokenized_text)
    print(number_words)
    print(unigram_vocab.most_common(20))
    print(bigram_vocab.most_common(20))

    for author_data in authors.values():
        author_unigram_frequency = Counter()
        author_bigram_frequency = Counter()
        for paragraph in author_data.paragraphs:
            author_unigram_frequency.update(paragraph.tokenized_text)
            author_bigram_frequency.update(zip(paragraph.tokenized_text[:-1], paragraph.tokenized_text[1:]))

        for bigram in bigram_vocab:
            if bigram in author_bigram_frequency:
                prob = author_bigram_frequency[bigram] / author_unigram_frequency[bigram[0]]
            else:
                prob = 0
            author_data.bigram_distribution[bigram] = prob
            
    print({author_id: author_data.bigram_distribution for author_id, author_data in authors.items()})
