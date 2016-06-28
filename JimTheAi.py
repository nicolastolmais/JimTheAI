import os
import sys
import random

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


import _thread
import pyaudio
import time
from gtts import gTTS
import pyglet

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 2

CLIENT_ACCESS_TOKEN = 'da2216150f6f401d892f02048b516925'


def input_thread(L):
    input()
    L.append(None)


def main():
    resampler = apiai.Resampler(source_samplerate=RATE)

    vad = apiai.VAD()

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.voice_request()

    request.lang = 'en'  # optional, default value equal 'en'

    def callback(in_data, frame_count, time_info, status):
        frames, data = resampler.resample(in_data, frame_count)
        state = vad.processFrame(frames)
        request.send(data)

        if (state == 1):
            return in_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paComplete

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=False,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()

    print ("Say! Press enter for stop audio recording.")

    try:
        L = []
        _thread.start_new_thread(input_thread, (L,))

        while stream.is_active() and len(L) == 0:
            time.sleep(0.1)

    except Exception:
        raise
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()

    print ("Wait for response...")
    response = request.getresponse()
    jsonAll = response.read().decode("utf-8")
    print(jsonAll)
    if(jsonAll.count("action") >= 1):
        actionStart = jsonAll.index("action") + 10
        actionEnd = jsonAll.index("actionIn") - 8
        action = jsonAll[actionStart:actionEnd]
    else:
        action = " "
    print(action)
    if(jsonAll.count("displayText") >= 1):
        speechStart = jsonAll.index("displayText")+13#fix to say all of sppech and not range
        speechEnd = jsonAll.index('"score"') -9
        speech = jsonAll[speechStart:speechEnd]
    else:
        speechStart = jsonAll.index("speech")+10#fix to say all of sppech and not range
        speechEnd = jsonAll.index('"score"') -9
        speech = jsonAll[speechStart:speechEnd]
    print(speech)
    if(action == "give_joke"):
        tellTheJoke()
    elif(action == "yahooWeatherForecast"):
        tellTheWeather(speech)
    else:
        print("excuse me")
    #figure out how to close app running
    
def tellTheJoke():
    f = open('jokefile.txt', 'r')
    jokes = []
    rand = random.randint(1,48)
    for line in f:
        jokes.append(line)
    randJoke = jokes[rand]
    tts = gTTS(text=randJoke, lang="en")
    tts.save("joke.mp3")
    music = pyglet.resource.media("joke.mp3")
    music.play()
    pyglet.app.run()
    f.close()
    
def tellTheWeather(speech):
    line = speech
    tts = gTTS(text=line, lang="en")
    tts.save("weather.mp3")
    music = pyglet.resource.media("weather.mp3")
    music.play()
    pyglet.app.run()
    return

if __name__ == '__main__':
    main()



    
