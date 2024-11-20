from wit import Wit
from tmdbv3api import TMDb, Search, Movie


def extract_intent(nlp_data):
    return nlp_data['intents'][0]['name']

def extract_entity(nlp_data, entity_name):
    entities = nlp_data.get('entities', {})
    entity_key = f"{entity_name}:{entity_name}"  # format 'entities': {'movieName:movieName'

    if entity_key in entities:
        for entity in entities[entity_key]:  # iterate through entity entries
            if entity.get('confidence', 0) >= 0.5:  # verify the confi level is enough
                return entity.get('value')

    return None


def movie_entity_from_intent(movie_name, intent):
    # initialize the TMDb object with my API key
    tmdb = TMDb()
    tmdb.api_key = '731f1dd6e50b36840dc855649f445a3b'

    # create Movie object to interact with the Movie endpoints
    movie_api = Movie()

    # let's try manual try out
    response = Search().movies(movie_name)  # I get the warning : search() is depreciated, use Search().movies()

    for movie in response:

        movie_name = movie.title

        release_year = movie.release_date[:4]

        plot = movie.overview

        if movie.poster_path:  # to avoid URL ending by None
            poster_link = f"https://image.tmdb.org/t/p/w500{movie.poster_path}"

        credits = movie_api.credits(movie.id)  # fetch movie credits using the movie ID
        director = None  # init
        if 'crew' in credits:
            for crew_member in credits['crew']:
                if crew_member['job'] == 'Director':
                    director = crew_member['name']
                    break  # exit when 1 director found

        main_cast = ""
        if 'cast' in credits:
            # print(credits)
            actor_names = ", ".join(actor['name'] for actor in credits['cast'])

            comma_position = [i for i, c in enumerate(actor_names) if c == ',']
            if len(comma_position) >= 5:  # keep only 5 for lisibility
                main_cast = actor_names[:comma_position[4]]

        if intent == "movieinfo":  # return plot & poster / releaseYear possible
            return plot, poster_link

        elif intent == "director":  # return director & poster
            return director, poster_link

        elif intent == "actors":  # return actors & poster
            return main_cast, poster_link

        elif intent == "releaseYear":  # return releaseYear & poster
            return release_year, poster_link

        else:  # if none of the intents match
            return None


def rephrase_response(intent, movie, entity, poster):
    if intent == "movieinfo":
        answer = f"🎬 The plot of the movie {movie} is : {entity}. To have a better look on the story, here is the poster: {poster}"

    elif intent == "director":
        answer = f"🎥 This is {entity} who directed the fantastical movie {movie}. Have a look at his vision by seeing the movie's poster : {poster}"

    elif intent == "actors":
        answer = f"👤 The movie {movie} is wonderful also thanks to the actors who played in it : {entity}. You can clearly recognize them on the movie's poster: {poster}"

    elif intent == "releaseYear":
        answer = f"🗓️ The movie {movie} was released in {entity}. The atmosphere of that era is reflected on its poster: {poster}"

    else:
        return None

    return answer


def main_movie(discord_input):
    # 2) Send it to the Wit.ai model
    wit_access_token = "XGC7EWF2AKPW4FVQ7PHASOZE7TO6ZS72"  # I define my access key to wit.ai
    client = Wit(wit_access_token)
    nlp_data = client.message(discord_input)
    print(nlp_data)

    # 3) Capture intent and entities (if any)
    # 4) Query TheMovieDB API to retrieve the required data
    intent_found = extract_intent(nlp_data)
    print(intent_found)

    movieName = extract_entity(nlp_data, "movieName")  # f° from section 2.3
    print(movieName)

    # releaseYear = extract_entity(nlp_data, "releaseYear")
    # print(releaseYear)

    entity, poster = movie_entity_from_intent(movieName, intent_found)
    # print(entity, poster)

    # 5) Rephrase the data into a full-sentence response
    reply = rephrase_response(intent_found, movieName, entity, poster)

    # 6) Reply to the user on Discord
    print(reply)
    return reply


# discord_input = "Tell me about The Spiderman (2007)"
# main_movie(discord_input)
