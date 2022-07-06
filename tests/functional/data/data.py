from data.models import Film, Genre, Person

genre_action = Genre(name="Action")
genre_sci_fi = Genre(name="Sci-Fi")
genre_documentary = Genre(name="Documentary")
genres = [genre_action, genre_documentary, genre_sci_fi]


person_fisher = Person(full_name="Carrie Fisher")
person_ford = Person(full_name="Harrison Ford")
person_lucas = Person(full_name="George Lucas")
person_burns = Person(full_name="Kevin Burns")
persons = [person_fisher, person_ford, person_lucas, person_burns]


film_1 = Film(
    title="Star Wars: Episode IV - A New Hope",
    imdb_rating=9.5,
    description="Star Wars: Episode IV - A New Hope Description",
    genres=[genre_action, genre_sci_fi],
    actors=[person_fisher, person_ford],
    writers=[person_lucas],
    directors=[person_lucas],
)
film_2 = Film(
    title="Star Wars: Episode V - The Empire Strikes Back",
    imdb_rating=9.4,
    description="Star Wars: Episode V - The Empire Strikes Back Description",
    genres=[genre_action, genre_sci_fi],
    actors=[person_fisher, person_ford],
    writers=[person_lucas],
    directors=[person_lucas],
)
film_3 = Film(
    title="Star Wars: Documentary",
    imdb_rating=9.3,
    description="Star Wars: Documentary Description",
    genres=[genre_documentary],
    actors=[person_fisher, person_ford, person_lucas],
    writers=[person_burns],
    directors=[person_burns],
)
films = [film_1, film_2, film_3]
