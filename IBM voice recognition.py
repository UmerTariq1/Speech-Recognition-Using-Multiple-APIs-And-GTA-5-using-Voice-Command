import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from threading import Thread
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full



###############################################
#### Initalize queue to store the recordings ##
###############################################
CHUNK = 1024
# Note: It will discard if the websocket client can't consumme fast enough
# So, increase the max size as per your choice
BUF_MAX_SIZE = CHUNK * 10
# Buffer to store audio
q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK)))

# Create an instance of AudioSource
audio_source = AudioSource(q, True, True)

###############################################
#### Prepare Speech to Text Service ########
###############################################

# Place your api key and URL here.
API_KEY = "XXXXXXXXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXX"
URL_S2T = "https://api.jp-tok.speech-to-text.watson.cloud.ibm.com/instances/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"


# initialize speech to text service
authenticator = IAMAuthenticator(API_KEY)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(URL_S2T)     # this line is not in IBM repo



# define callback for the speech to text service
class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        # pass
        print( "\n\n\n Final predicted text is : " + transcript[0]["transcript"] , end="\n\n\n")
        print("\n Final predicted text's confidence is : ",transcript[0]["confidence"])

    def on_connected(self):
        print('Connection was successful')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

    def on_listening(self):
        print('Service is listening')

    #Returns interim results or maximum alternatives from the service when those responses are requested.
    def on_hypothesis(self, hypothesis):
        # pass
        print("\n Non Final output is : " , hypothesis  )

    #Returns all response data for the request from the service.
    def on_data(self, data):
        pass
        # print("data : " , data)

    def on_close(self):
        print("Connection closed")

# this function will initiate the recognize service and pass in the AudioSource
def recognize_using_weboscket(*args):
    mycallback = MyRecognizeCallback()
    speech_to_text.recognize_using_websocket(audio=audio_source,
                                             content_type='audio/l16; rate=44100',
                                             interim_results=True,
                                             model="en-US_BroadbandModel",
                                            #  keywords=KEYWORD_PHRASES,  #keywords to focus on
                                            #  keywords_threshold=0.1,            #if a keyword's probability is more than this threashold then that is 'outputted'
                                             recognize_callback=mycallback
    )
 

###############################################
#### Prepare the for recording using Pyaudio ##
###############################################

# Variables for recording the speech
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# define callback for pyaudio to store the recording in queue
def pyaudio_callback(in_data, frame_count, time_info, status):
    try:
        q.put(in_data)
    except Full:
        pass # discard
    return (None, pyaudio.paContinue)

# instantiate pyaudio
audio = pyaudio.PyAudio()

# open stream using callback
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=pyaudio_callback,
    start=False
)

#########################################################################
#### Start the recording and start service to recognize the stream ######
#########################################################################

print("IBM Watson Speech To Text API")
print("----------------------------- \n\n")

stream.start_stream()

try:
    recognize_thread = Thread(target=recognize_using_weboscket, args=())
    recognize_thread.start()

    while True:
        pass
except KeyboardInterrupt:
    # stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    audio_source.completed_recording()