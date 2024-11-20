import discord

from weather_bot import *
from movie_bot import *


# Step 1 : Implement an instance of Client

TOKEN = "MTMwNjI1NDYzNDg5MzE4MDkyOQ.GNZk3s.7jJSwTdDn5bj7LwhySSyMQ95MTZyRhzRurLquE"  # my bot token
class MyClient (discord . Client):
    async def on_ready(self):
        print('Logged in as ' + str(self.user.name))
        print('The chatbot Id : ' + str(self.user.id))

    # Step 2 : Receiving and sending messages from my Discord server & chatbot doesn't interact with its own messages

    async def on_message(self, message):

        if message.author == self.user:  # for the bot itself message -> ignore
            return

        if message.content.lower() == "how are you ?":  # to understand the message even if it is capital letters
            await message.channel.send("Fine and you ? The weather is cool today ☀️")

        else:
            # no need to do a loop anymore -> Discord already perform its own question-answer loop

            user_intention = new_intent_search(message.content.lower())
            print(message.content)
            print(user_intention)

            # no more quit option

            # 4) Call weather functions if intention detected is a question about weather
            if user_intention == 'weather question':
                city_time = createEntities(message.content)
                city = city_time['city']
                time = city_time['time']

                weather_info_json = getWeather(city, time)
                weather_response = detailed_temperature_response(weather_info_json)

                # NEW 1 : Get the image of the city named by the user when asking the weather
                city_image_url = get_city_image(city)  # get the image via Unsplash

                if city_image_url:  # embedded response containing the text and image
                    embed = discord.Embed(
                        title=f"Weather in {city}",
                        description=weather_response,
                        color=0x1E90FF  # my favourite color :)
                    )
                    embed.set_image(url=city_image_url)

                    await message.channel.send(embed=embed)  # send it into the server

                else:
                    await message.channel.send(weather_response)  # only the text if no image is found

            # 2) Define a default response to the undefined intention from the user.
            elif user_intention == 'undefined':

                reply = main_movie(message.content)

                if reply:
                    await message.channel.send(reply)
                else:
                    await message.channel.send("I did not understand. Could you tell me something else ?")

            else:
                # Respond with the generic chatbot answer -> by searching intentions in the dico
                response = chatbot_response(user_intention)

                # NEW 2 : Saying username for greetings
                if user_intention == 'greetings':
                    greeting_name = random.choice(["Hello", "Hey", "Hi"])
                    response = f"{greeting_name} {message.author.name} ☀️ ! {response}"
                if user_intention == 'ending':
                    ending_name = random.choice(["Goodbye", "Bye", "Catch you later"])
                    response = f"{ending_name} {message.author.name} 🌜️ ! {response}"

                # NEW 3 : Display a GIF when thanking, apologing or helping
                if user_intention == 'thanks' or user_intention == 'apology' or user_intention == 'help':
                    gif_url = get_gif_url(user_intention)
                    if gif_url:
                        await message.channel.send(gif_url)

                await message.channel.send(response)


client = MyClient(intents=discord.Intents.default())
client.run(TOKEN)

