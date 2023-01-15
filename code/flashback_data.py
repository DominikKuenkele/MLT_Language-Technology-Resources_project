import datetime
import json
from dataclasses import dataclass, field

from imm_loader import ParagraphSample


@dataclass(kw_only=True)
class Post:
    post_id: str
    date: datetime
    author_id: str
    forum: str = ''

    def __hash__(self) -> int:
        return hash((self.post_id))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Post):
            return self.post_id == __o.post_id
        return False


@dataclass(kw_only=True)
class Sentence:
    post: Post
    paragraph: int = -1
    sentence: int = -1
    tokens: list[str] = field(default_factory=list)
    pos: list[str] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash((self.post, self.paragraph, self.sentence))

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Sentence):
            return self.post == __o.post and self.paragraph == __o.paragraph and self.sentence == __o.sentence
        return False


@dataclass
class AuthorData:
    sentiment: float = -1
    unigram_distribution: list[int] = field(default_factory=list)
    bigram_distribution: list[int] = field(default_factory=list)
    paragraphs: list[ParagraphSample] = field(default_factory=list)


def obj_dict(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj.__dict__


def load_posts(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        json_dict = json.load(f)

    posts = []
    for item in json_dict:
        posts.append(Post(
            post_id=item['post_id'],
            date=datetime.datetime.fromisoformat(item['date']),
            author_id=item['author_id'],
            forum=item['forum']
        ))
    return posts


def save_posts(posts: list[Post], file: str):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, default=obj_dict, ensure_ascii=False)


def load_sentences(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        json_dict = json.load(f)

    sentences = []
    for item in json_dict:
        post = Post(
            post_id=item['post']['post_id'],
            date=datetime.datetime.fromisoformat(item['post']['date']),
            author_id=item['post']['author_id'],
            forum=item['post']['forum']
        )
        sentences.append(Sentence(
            post=post,
            paragraph=item['paragraph'],
            sentence=item['sentence'],
            tokens=item['tokens'],
            pos=item['pos']
        ))

    return sentences


def save_sentences(sentences, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(sentences, f, default=obj_dict, ensure_ascii=False)
