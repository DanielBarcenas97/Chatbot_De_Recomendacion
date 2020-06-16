# import the module 
import speech_recognition as sr 
# create the recognizer 
r = sr.Recognizer() 
# define the microphone 
mic = sr.Microphone(device_index=0) 
# record your speech 
with mic as source: 
   audio = r.listen(source) 
# speech recognition 
result = r.recognize_google(audio)
# export the result 
with open('my_result.txt',mode ='w') as file: 
   file.write("Recognized text:") 
   file.write("\n") 
   file.write(result) 
print("Exporting process completed!")

try:
    print("You said: " + r.recognize_google(audio))
except Exception as e:
    print("Error: " + str(e))
