import pickle
from time import sleep

from flashback_data import load_posts, save_posts
from imm_loader import DocumentLoader
from web_scraper import ForumLoader


def load_imm():
    documents = DocumentLoader("data/swe-absa-bank-imm/D_annotation.tsv")
    print("loaded (imm):", len(documents.samples))

    return [document.document_id for document in documents.samples]


def load_absa():
    with open("index_absa.pickle", "rb") as f:
        absa_posts = pickle.load(f)

    print("loaded (absa):", len(absa_posts))
    return absa_posts


def save(all_posts):
    print("indexed:", len(all_posts))

    save_posts(all_posts, "index_absa_metadata.json")


if __name__ == "__main__":
    saved = load_posts("index_absa_metadata.json")

    all_posts = set(saved)
    print("saved_posts:", len(all_posts))
    ids = {post.post_id for post in all_posts}
    print("ids:", len(ids))

    time_out = 10
    scraper = ForumLoader("https://www.flashback.org/")

    posts = load_absa()
    # posts = load_imm()

    max_tries = 2
    for post in posts:
        for t in range(max_tries):
            try:
                post_id = post.split("flashback-")[-1]
                if post_id not in ids:
                    scraper.fetch_post(post_id)
                break
            except (AttributeError, ConnectionRefusedError):
                print(f"Try: {t + 1}")
                all_posts.update(scraper.posts)
                save(all_posts)

                print(f"sleeping for {time_out}s...")
                sleep(time_out)
                if time_out < 60:
                    time_out += 5

    save(all_posts)
