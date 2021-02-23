from .contentbased_filtering import update_cache_for_item_based_recommendations
from .unification import fetch_user_recommendations
from threading import Thread

class Recommender:
    @staticmethod
    def fetch_next_cocktail(user):
        fetch_user_recommendations(user.id, only_first=True)

    @staticmethod
    def fetch_cocktails(user):
        fetch_user_recommendations(user.id, only_first=False)

    @staticmethod
    def on_review_changed(user, review, old_review=None):
        thread = Thread(target=update_cache_for_item_based_recommendations, args=(user.id, review, old_review))
        thread.start()
