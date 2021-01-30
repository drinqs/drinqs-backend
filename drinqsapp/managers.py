from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from django.db import models

class CocktailManager(models.Manager):
    def search(self, search_term):
        if not search_term:
            return self.get_queryset().all()

        search_query = SearchQuery(search_term, config="english")
        search_vectors = (
            SearchVector("name", weight="A", config="english")
            + SearchVector(
                StringAgg("ingredients__name", delimiter=" "), weight="B", config="english"
            )
        )
        search_rank = SearchRank(search_vectors, search_query)
        trigram_similarity = TrigramSimilarity("name", search_term)

        return (
            self.get_queryset()
            .annotate(search=search_vectors)
            .filter(search=search_query)
            .annotate(rank=search_rank + trigram_similarity)
            .order_by("-rank")
        )
