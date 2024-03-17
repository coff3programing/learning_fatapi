
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import HTMLResponse, JSONResponse

from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()


class Movies(BaseModel):
    """This class represents a model for storing information about movies."""
    id: int
    title: str = Field(max_length=25, min_length=5)
    overview: str = Field(min_length=6)
    year: int = Field(ge=1900)
    rating: Optional[float] = None
    category: str = Field(max_length=55, min_length=2)


class Config:
    """This class called Config is used to indicate the default values"""
    schema_extra = {
        'example': {
            'id': 1,
            'title': 'Write the title of the Movie',
            'overview': "Write the description of your Movie",
            'year': 1991,
            'rating': 8.9,
            'category': 'Drama'
        }
    }


movies_list = [
    Movies(
        id=1,
        title='The Godfather: Part II',
        overview="The aging patriarch of an organized crime family becomes an insistent conscripter in order to control the family through the use of dream-sharing technology.",
        year=1972,
        rating=8.9,
        category='Drama'
    ),
    Movies(
        id=2,
        title='Star Wars',
        overview="A space opera set “a long time ago in a galaxy far, far away,”  the film centres on Luke Skywalker (played by the then relatively unknown Mark Hamill), a young man who finds himself embroiled in an interplanetary war between an authoritarian empire and rebel forces.",
        year=1977,
        rating=8.9,
        category='Action'

    )
]


@app.get('/', tags=['Home'], status_code=200)
async def home():
    """
    The `index` function returns an HTMLResponse with the text "Pong🥎!".
    :return: The `index` function is returning an HTMLResponse
    object with the content "<b>Pong🥎!</b>".
    """
    return HTMLResponse("<b>Pong🥎!</b>")


@app.get(
    '/movies',
    tags=['Movies'],
    response_model=List[Movies],
    status_code=200
)
async def get_movies() -> List[Movies]:
    """
    This Python function `get_movies` asynchronously retrieves
    a list of movies.
    :return: The function `get_movies()` is returning a list
    of `Movies` objects.
    """
    return movies_list


@app.get(
    '/movies/{id}',
    tags=['Movies'],
    response_model=Movies,
    status_code=200
)
async def get_movie(id: int = Path(ge=1, le=2000)) -> Movies:
    """
      Get a movie based on your id
    """
    return search_movie(id)


@app.get(
    '/movies',
    tags=['Movies'],
    response_model=List[Movies],
    status_code=200
)
async def get_categories(
    category: str = Query(min_length=3, max_length=22)
) -> List[Movies]:
    """Get a movie based on your category"""
    return search_category(category)

# Post


@app.post('/movies', tags=["Movies"], response_model=dict, status_code=201)
async def create_movie(movies: Movies) -> dict:
    """Register a new movie"""

    is_equal = type(search_movie(movies.id)) == Movies

    if is_equal:
        return HTTPException(
            status_code=409,
            detail={"error": "Movie already exists"}
        )
    movies_list.append(movies)
    return movies


@app.put('/movies/{id}', tags=['Movies'], response_model=dict, status_code=200)
async def update_movie(id: int, movies: Movies) -> dict:
    """Function update movies."""
    found = False

    for i, saved_movie in enumerate(movies_list):
        if saved_movie.id == id:
            movies_list[i] = movies
            found = True

    if not found:
        raise HTTPException(
            status_code=404,
            detail={"error": "The movie could not be updated"}
        )
    return movies


@app.delete(
    '/movies/{id}',
    tags=['Movies'],
    response_model=dict,
    status_code=200
)
async def delete_movie(id: int = Path(ge=1, le=2000)) -> dict:
    """Function delete movies."""
    found = False

    for i, saved_movie in enumerate(movies_list):
        if saved_movie.id == id:
            del movies_list[i]
            found = True

    if not found:
        raise HTTPException(
            status_code=404,
            detail={"error": "The movie could not be deleted"}
        )

    return JSONResponse(
        status_code=200,
        content={
            "message":
            f"The movie with the id '{id}', has been successfully deleted"
        }
    )

# Validations


def search_category(category: str):
    movie = filter(lambda el: el.category == category, movies_list)
    try:
        return list(movie)[0]
    except:
        raise HTTPException(status_code=404, detail={
                            "error": "Categories not found"})


def search_movie(id: int):
    movie = filter(lambda el: el.id == id, movies_list)
    try:
        return list(movie)[0]
    except:
        return HTTPException(status_code=404, detail={"error": "Movie not found"})
