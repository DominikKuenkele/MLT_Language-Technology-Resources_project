import pickle
from datetime import datetime
from glob import glob
from xml.etree import ElementTree

from flashback_data import Post, Sentence, save_sentences


def save(all_sentences_set, forum):
    print(forum, len(all_sentences_set))
    if len(all_sentences_set) > 0:
        print(list(all_sentences_set)[0])
    save_sentences(list(all_sentences_set), f"data/saved/all_sentences_{forum}.json")


if __name__ == "__main__":
    with open("index_absa_author.pickle", "rb") as f:
        saved_posts: list[Post] = pickle.load(f)

    authors = set()
    for post in saved_posts:
        authors.add(post.author_id)

    for file in glob("C://Users/domin/Downloads/*.xml"):
        forum = file.split("\\")[-1].removeprefix("flashback-").removesuffix(".xml")

        all_sentences_set = set()

        with open(file, "r", encoding="utf-8") as f:
            for index, line in enumerate(f):
                stripped_line = line.strip()
                if stripped_line.startswith("<text"):
                    author_start_index = stripped_line.find('userid="')
                    if author_start_index > -1:
                        author_start_index = author_start_index + 8
                        author_end_index = stripped_line.find('"', author_start_index)
                        author_id = stripped_line[author_start_index:author_end_index]
                        if f"u{author_id}" in authors:
                            date_start_index = stripped_line.find('date="')
                            if date_start_index > -1:
                                date_start_index = date_start_index + 6
                                date_end_index = stripped_line.find(
                                    '"', date_start_index
                                )
                                date_string = stripped_line[
                                    date_start_index:date_end_index
                                ]
                                date = datetime.strptime(date_string, "%Y-%m-%d %H:%M")

                            postid_start_index = stripped_line.find(' id="')
                            if postid_start_index > -1:
                                postid_start_index = postid_start_index + 5
                                postid_end_index = stripped_line.find(
                                    '"', postid_start_index
                                )
                                post_id = stripped_line[
                                    postid_start_index:postid_end_index
                                ]

                            xml = line
                            skip = 0
                            while "</text>" not in xml:
                                xml += next(f)
                                skip += 1

                            root = ElementTree.fromstring(xml)
                            for paragraph_number, paragraph in enumerate(
                                root.findall("paragraph")
                            ):
                                for sentence_number, sentence in enumerate(
                                    paragraph.findall("sentence")
                                ):
                                    tokens = []
                                    pos = []
                                    for token in sentence.iter("token"):
                                        tokens.append(token.text)
                                        pos.append(token.get("pos"))

                                    post = Post(
                                        post_id=post_id,
                                        date=date,
                                        author_id=f"u{author_id}",
                                        forum=forum,
                                    )

                                    all_sentences_set.add(
                                        Sentence(
                                            post=post,
                                            paragraph=paragraph_number,
                                            sentence=sentence_number,
                                            tokens=tokens,
                                            pos=pos,
                                        )
                                    )

                            index += skip

                if index % 1_000_000 == 0:
                    save(all_sentences_set, forum)
                    print(index)
        save(all_sentences_set, forum)
