import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr

from recomendarPelicula import recomendar
from recomendarPelicula import get_index_from_title,get_title_from_index

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

def tts(text,lang,name_file):
    file = gTTS(text = text, lang = lang)
    filename = name_file
    file.save(filename)


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json,msg):
    pelis = []
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if (i['tag']== 'recibirpelicula'):
            pelicula = msg.replace("me gusta la película de ","")
            print(pelicula)
            resp = recomendar(pelicula)
            j=0
            for element in resp:
                print (get_title_from_index(element[0]))
                result = get_title_from_index(element[0])
                pelis.append(result)
                j=j+1
                if j>10:
                    return pelis
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            return result

    

def chatbot_response(msg):
    ints = predict_class(msg, model)
    predict = float (ints[0]['probability'])
    print(ints[0])
    if(predict > 0.80):
        res = getResponse(ints, intents,msg)
        print(res)#Respuesta
    else:
        res = random.choice(["Disculpa no puedo entenderte", "Porfavor dame mas información", "No entendi perdon","Disculpa no entendi","Puedes explicarme mejor"])
    return res

#Me gusta la pelicula de spiderman
#Creating GUI with tkinter
import tkinter
from tkinter import *

def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "Yo: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
        res = chatbot_response(msg)
        print(type(res))
        if (isinstance(res, list)):
            for i in res:
                ChatLog.insert(END, "Arti: " + i + '\n\n')
        else:
            ChatLog.insert(END, "Arti: " + res + '\n\n')
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
    if msg == 'Quit':
        base.destroy()

def sendtalk():
    r = sr.Recognizer() 
    with sr.Microphone() as source:
        print('Speak Anything : ')
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language='es-mx')
            print('You said: {}'.format(text))
        except:
            print('Sorry could not hear')
    
    msg = text
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "Yo: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
        res = chatbot_response(msg)
        print(type(res))
        if (isinstance(res, list)):
            for i in res:
                NOMBRE_ARCHIVO = "voz.mp3"
                ChatLog.insert(END, "Arti: " + i + '\n\n')
                tts(res,"ES", NOMBRE_ARCHIVO)
                playsound(NOMBRE_ARCHIVO)
        else:
            ChatLog.insert(END, "Arti: " + res + '\n\n')
            NOMBRE_ARCHIVO = "voz.mp3"
            tts(res,"ES", NOMBRE_ARCHIVO)
            playsound(NOMBRE_ARCHIVO)
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
    if msg == 'Quit':
        base.destroy()

base = Tk()
base.title("Arti Chatbot")
base.geometry("710x800")
base.resizable(width=FALSE, height=FALSE)
base.configure(background='#0059b3')

logo = PhotoImage(file='bot.png')
labelLogo = Label(base, image=logo)
labeltext = Label(base, text = "Hola soy Arti",font=("Roboto",18,'bold'),bg="#e8eaf6",)
labelLogo.grid(row=0, column=2, columnspan=2, rowspan=2,
               sticky=W+E+N+S, padx=5, pady=5)

#Create Chat window
ChatLog = Text(base, bd=0, bg="#e8eaf6", height="8", width="160", font="Roboto",)

ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart",bg="#e8eaf6")
ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message
SendButton = Button(base, font=("Roboto",12,'bold'), text="Enviar", width="12", height=3,
                    bd=0, bg="red", activebackground="#3c9d9b",fg='#0059b3',
                    command= send )

SendVoice = Button(base, font=("Roboto",12,'bold'), text="Hablar", width="12", height=3,
                    bd=0, bg="black", activebackground="#3c9d9b",fg='#0059b3',
                    command= sendtalk )
#Create the box to enter message
EntryBox = Text(base, bd=0, bg="#e8eaf6",width="60", height="3", font="Arial")
#EntryBox.bind("<Return>", send)


labeltext2 = Label(base, text = "Chatbot de recomendacion de peliculas!",font=("Roboto",18,'bold'),bg="#0059b3")

#Place all components on the screen
labelLogo.place(x=250,y=20,width=200, height=180)
labeltext.place(x=300,y=220)
scrollbar.place(x=685,y=260, height=400)
ChatLog.place(x=6,y=260, height=400, width=690)
EntryBox.place(x=130, y=680, height=80, width=450)
SendButton.place(x=6, y=680, height=80)
SendVoice.place(x=590, y=680, height=80)
labeltext2.place(x=200,y=0)

base.mainloop()






