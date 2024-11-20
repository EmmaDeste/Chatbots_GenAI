import re  # library to test regex
import nltk
from nltk.corpus import wordnet as wn
from spellchecker import SpellChecker
import requests
import random
from datetime import datetime

API_KEY = 'YMAQuHpAQpDjBSOzvmtZ7Y1VBU9nFCjM'

weather_questions_dict = {
    'get weather': 'What is the weather like in',
    'get temperature': 'Which temperature in',
    'get night hour': 'What is the sunrise hour in'
}

weather_keywords = {
    'weather question': ['weather', 'rain', 'temperature', 'sunrise', 'cold']
}

responses = {
    'greetings': [
        "How can I help you today?",
        "You look well today!",
        "Welcome here!",
        "How can I assist you today?"
    ],
    'time': [
        "The current time is 3:45 PM.",
        "It's 10:30 in the morning right now.",
        "The time is 8:00 AM, bright and early!",
        "It’s 6:45, almost time for dinner!",
        "It's 1:00 PM, right after lunch!"
    ],
    'ending': [
        "Have a great day!",
        "Take care, hope to chat soon!",
        "Feel free to come back anytime!",
        "Best wishes!"
    ],
    'thanks': [
        "You're welcome! 😊",
        "No problem at all!",
        "Glad I could help!",
        "You're very welcome!",
        "Anytime! Happy to help!"
    ],
    'apology': [
        "Sorry about that! How can I assist you better?",
        "My bad! Please forgive me.",
        "I apologize for the inconvenience!",
        "Oops, I’m sorry. Let me fix that!"
    ],
    'help': [
        "How can I assist you today?",
        "What do you need help with?",
        "I'm here to help! How can I assist you?",
        "Please tell me how I can help.",
        "What’s on your mind? I can help!"
    ],
    'affirmation': [
        "Yes, absolutely!",
        "Of course we agree!",
        "Sure thing!",
        "Definitely!",
        "For sure!"
    ],
    'location': [
        "I’m here to help you. Where exactly are you trying to go?",
        "Can you specify the location?",
        "Could you give me more details about the place?",
        "Where exactly are you looking for?",
        "What’s the address you need help with?",
    ]
}

intent_keywords = {
    'greetings': ['hello', 'howdy', 'hi', 'hullo', 'how do you do', 'hey'],
    'time': ['time', 'clock', 'what time', 'hours', 'minute', 'second'],
    'ending': ['goodbye', 'bye', 'see you', 'take care', 'farewell', 'catch you later'],

    'thanks': ['thank you', 'thanks', 'thanks a lot', 'many thanks', 'much appreciated'],
    'apology': ['sorry', 'my bad', 'apologies', 'excuse me', 'pardon me', 'i apologize'],
    'help': ['help', 'assist', 'support', 'need assistance', 'help me'],
    'affirmation': ['yes', 'yeah', 'yep', 'of course', 'definitely', 'sure'],
    'location': ['where', 'located', 'find', 'address', 'place']
}


def extend_1keyword(keyword):
    synonyms = set()

    # see main functions described in https://www.nltk.org/howto/wordnet.html
    for syn in wn.synsets(keyword):
        for lemma in syn.lemmas():
            lemma_name = lemma.name().lower()  # extract name and convert to lowercase

            # Avoid words with special characters or accented letters
            if re.match(r'^[a-zA-Z0-9_]+$', lemma_name):
                synonyms.add(lemma_name)

    synonyms = list(synonyms)
    return synonyms


def extend_keywords(my_keywords_dict):
    """
    This function extends the keywords dictionary by adding synonyms for each keyword.
    """
    extended_keywords_dict = {}  # initializing the new dictionnary

    for intent, keywords in my_keywords_dict.items():
        extended_keywords = set(keywords)  # start with original keywords

        # For each keyword, find synonyms in WordNet and add them to the set
        for keyword in keywords:
            synonyms_keyword = extend_1keyword(keyword)
            extended_keywords.update(synonyms_keyword)  # add synonyms to the set

        # Store the extended keyword list for this intent
        extended_keywords_dict[intent] = list(extended_keywords)

    return extended_keywords_dict


def word_to_regex(keywords_dict):
    regex_dict = {}
    regex_wordBegin = '.*\\b'
    regex_wordEnd = '\\b.*|'  # add | in the pattern but remove the last occurence at the end of the loop

    for intent, keywords in keywords_dict.items():
        keyword_reg = ''

        for keyword in keywords:

            if '_' in keyword:  # nobody will write underscore when typing, so I remove this sign from keywords
                keyword = keyword.replace('_', ' ')

            keyword_reg = keyword_reg + regex_wordBegin + keyword + regex_wordEnd

        keyword_reg = keyword_reg[:-1]  # remove the last | to avoid a syntax error

        regex_dict.update({intent: keyword_reg})

    return regex_dict


def correct_typo(user_words_list):
    spell = SpellChecker()

    user_words_corrected = []

    # find those words that may be misspelled
    misspelled = spell.unknown(user_words_list)

    if misspelled:  # corresponding to a not empty list
        for word in misspelled:
            user_words_corrected.append(spell.correction(word))
    for word in user_words_list:
        if word not in misspelled:  # so that I have all the words from the user, but not twice
            user_words_corrected.append(spell.correction(word))

    return user_words_corrected


# now extend with my WordNet function
extended_keywords_dict = extend_keywords(intent_keywords)
extended_weather_dict = extend_keywords(weather_keywords)
extended_keywords_dict.update(extended_weather_dict)

regex_dict = word_to_regex(extended_keywords_dict)


def chatbot_response(user_intention):  # define bot looping responses
    return random.choice(responses[user_intention])  # return a random response for the matched intent


def regex_capture_groups(questions_dict):
    regex_dict = {}
    sentence_reg = ''

    for intent, sentence in questions_dict.items():
        sentence_reg = sentence + ' (?P<city>[a-zA-Z\s]+) (?P<time>tomorrow|today).*'
        # \s -> enable space between alphanumeric => catch cities with 2 words

        regex_dict.update({intent: sentence_reg})

    return regex_dict

weather_questions_regex = regex_capture_groups(weather_questions_dict)

def matchPattern_weather(user_msg):
    # si non -> city et time not known
    city = 'undefined'
    time = 'undefined'

    # loop dans le pattern pour trouver si 1 entity correspondant dans le dico -> et alors remplacer le undefined de défaut
    for intent, regex_get_entity in weather_questions_regex.items():
        # print("-> ", regex_get_entity)

        match = re.search(regex_get_entity, user_msg)
        if match != None:
            city = match.groupdict()['city']  # equivalent to m.group(1) here
            time = match.groupdict()['time']

    return city, time


def createEntities(user_msg):  # aim to extract entities from the user message

    entities_dict = {}

    city, time = matchPattern_weather(user_msg)

    entities_dict = {'city': city, 'time': time}

    return entities_dict


def matchPattern(user_msg):
    # in order to pass the message to pyspellchecker correct_typo, I need to parse it into a list of words
    user_msg_list = user_msg.split()
    user_msg_clean = correct_typo(user_msg_list)
    # print(user_msg_clean)

    # si non -> intention de undefined
    found_intent = 'undefined'

    for word in user_msg_clean:  # pour tous les mots du message

        # loop dans le pattern pour trouver si 1 keyword correspondant dans le dico -> et alors remplacer le undefined de défaut
        for intent, regex_keywords in regex_dict.items():
            # si oui -> renvoie la key de ce keyword
            match = re.search(regex_keywords, word)
            if match != None:
                found_intent = intent

    return found_intent


def new_intent_search(user_msg):
    user_intention = matchPattern(user_msg)
    # print("-> found intention :", user_intention)

    if user_intention != 'undefined' and user_intention != 'weather question':
        response = chatbot_response(user_intention)
        print(f"Chatbot: {response}")

    return user_intention


def getWeather(location, date):
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": location,
        "apikey": API_KEY,
        "timesteps": "1d",
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:  # OK
            data = response.json()

            # toodo : comprendre cette partie
            # Access fields dynamically based on the response structure
            # Adjusting the parsing logic based on the printed data
            forecast = data.get('timelines', {}).get('daily', [{}])[0]
            values = forecast.get('values', {})
            temp_celsius = values.get('temperatureAvg', "No temperature data")
            humidity = values.get('humidityAvg', "No humidity data")

            return {
                "Location": location,
                "Date": date,
                "Temperature (°C)": temp_celsius,
                "Humidity (%)": humidity
            }

        elif response.status_code == 400:  # Bad request
            return {"error": "Bad Request. the request was invalid."}

        elif response.status_code == 404:  # Not found
            return {"error": "Location not found. Please check your town's name or location coordinates or."}

        else:
            return {"error": f"An unexpected error occurred. Status code: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def process_weather_response(weather_info_json):
    response = f"{weather_info_json['Date']} in {weather_info_json['Location']} you have {weather_info_json['Temperature (°C)']} °C and {weather_info_json['Humidity (%)']} % humidity"
    return response


def detailed_temperature_response(weather_info_json):
    temperature = weather_info_json['Temperature (°C)']
    city = weather_info_json['Location']

    # add color with the syntax described in https://stackoverflow.com/questions/68843711/how-to-return-colored-text-from-a-function
    # adding color is so difficult on Discord, so I return a photo instead
    if temperature < 0:
        # return f'\033[34m🥶 It is very cold in {city} with only {temperature} °C, hope you enjoy ice skating\033[0m'
        return f'🥶 It is very cold in {city} with only {temperature} °C, hope you enjoy ice skating'
    else:
        if temperature > 30:
            return f'🥵 It is kind of hot in {city} with {temperature} °C, so you would better drink water'
        else:
            if temperature < 15:
                return f'🙂 It is a little bit cold in {city} with {temperature} °C, but no worries about snow'
            else:
                return f'🌸 It is cool today, {temperature} °C in {city}. Have fun!'


def main_API():  # not used anymore, I create a new one in my bot class MyClient
    print("Hi! I am Bot. To end conversation say 'bye' or 'leave'.")

    while True:  # -> pas besoin vu que Discord fait déjà une boucle de question réponse
        # => switching loop that keeps in place the flow of the conversation

        # 1) Match your chatbot response to the user input and ask for its next message.
        user_msg = input("User : ")
        user_intention = new_intent_search(user_msg)

        # 3) For the exit case, reply back to the user and exit the console.
        if user_intention == 'ending':
            response = chatbot_response(user_intention)
            break

        # 2) Define a default response to the undefined intention from the user.
        if user_intention == 'undefined':
            print("Chatbot: I did not understand. Could you tell me something else ?")
            # -> take a new message from user : easy, it loop again in the while

        # 4) New : Call weather functions if intention detected is a question about weather
        if user_intention == 'weather question':
            city_time = createEntities(user_msg)

            # result = getWeather("Paris", today)
            weather_info_json = getWeather(city_time['city'], city_time['time'])
            # print(result)
            weather_response = detailed_temperature_response(weather_info_json)
            # print(weather_response)


# **********************************************************************************************

# NEW 1 : Get the image of the city named by the user when asking the weather
def get_city_image(city_name):
    access_key = "gif64E9A_epFFSw-i4Q5xGAJBdmoVYGD8X0006OA_bE"
    url = f"https://api.unsplash.com/photos/random?query={city_name}&client_id={access_key}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        image_url = data['urls']['regular']  # extract image URL from the JSON response
        return image_url
    else:
        print("Error of recuperation of Unsplash image :", response.status_code)
        return None

# NEW 3 : Display a GIF when thanking, apologing or helping
def get_gif_url(search_term):
    tenor_api_key = 'AIzaSyBJjxp8JMoxHBM6Wr2DVgqT99mdPsegFDU'
    url = f"https://tenor.googleapis.com/v2/search?q={search_term}&key={tenor_api_key}&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['media_formats']['gif']['url']
    return None
