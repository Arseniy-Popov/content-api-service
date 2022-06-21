from elasticsearch_dsl import Search


def paginate(search: Search, page_number: int, page_size: int) -> Search:
    return search[(page_number - 1) * page_size : page_number * page_size]
