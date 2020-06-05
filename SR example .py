import speech_recognition as sr
import pyttsx3 
import datetime
import json

r = sr.Recognizer()  


print("Google (without google cloud) Speech To Text API (with SpeechRecognition library)")
print("-------------------------------------------------------------------------------- \n\n")

while(True):    
    # Exception handling to handle 
    # exceptions at the runtime 
    try: 
          
        # use the microphone as source for input. 
        with sr.Microphone() as source: 
            print("listening")

            # wait for a second to let the recognizer 
            # adjust the energy threshold based on 
            # the surrounding noise level  
            r.adjust_for_ambient_noise(source) 

            start = datetime.datetime.now()  
            #listens for the user's input  
            audio = r.listen(source,phrase_time_limit=1) 
            MyText = r.recognize_google(audio,language="en-US") 


            end = datetime.datetime.now()

            MyText = MyText.lower() 
            print("\n Final predicted text is :",MyText, end="\n\n\n")
              
    except sr.WaitTimeoutError as e:
        print("Timeout; {0}".format(e))
    except sr.RequestError as e: 
        print("Could not request results; {0}".format(e)) 
          
    except sr.UnknownValueError: 
        print("unknown error occured")