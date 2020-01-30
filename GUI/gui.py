from tkinter import *
import requests
import json

class GUI(object):
    def __init__(self, master=None):
        self.fontePadrao = ("Arial", "10", "bold")

        # CONTAINERS
        self.primeiroContainer = Frame(master)
        self.primeiroContainer["pady"] = 10
        self.primeiroContainer.pack()
  
        self.segundoContainer = Frame(master)
        self.segundoContainer["padx"] = 20
        self.segundoContainer.pack()
  
        self.terceiroContainer = Frame(master)
        self.terceiroContainer["padx"] = 20
        self.terceiroContainer.pack()
  
        self.quartoContainer = Frame(master)
        self.quartoContainer["padx"] = 20
        self.quartoContainer.pack()

        self.quintoContainer = Frame(master)
        self.quintoContainer["padx"] = 20
        self.quintoContainer.pack()

        self.sextoContainer = Frame(master)
        self.sextoContainer["pady"] = 5
        self.sextoContainer["padx"] = 20
        self.sextoContainer.pack()
  
        # GUI TITLE 
        self.titulo = Label(self.primeiroContainer, text="DOJOT -> DEVICE")
        self.titulo["font"] = ("Arial", "10", "bold")
        self.titulo.pack()

        # HOST
        self.hostLabel = Label(self.segundoContainer,text="Host:", font=self.fontePadrao)
        self.hostLabel.pack(side=LEFT)
  
        self.host = Entry(self.segundoContainer)
        self.host["width"] = 30
        self.host["font"] = self.fontePadrao
        self.host.pack(side=LEFT)

        # PORT
        self.portLabel = Label(self.segundoContainer,text="Port:", font=self.fontePadrao)
        self.portLabel.pack(side=LEFT)
  
        self.port = Entry(self.segundoContainer)
        self.port["width"] = 30
        self.port["font"] = self.fontePadrao
        self.port.pack(side=LEFT)

        # TOKEN
        self.tokenLabel = Label(self.terceiroContainer,text="Token:", font=self.fontePadrao)
        self.tokenLabel.pack(side=LEFT)
  
        self.token = Entry(self.terceiroContainer)
        self.token["width"] = 30
        self.token["font"] = self.fontePadrao
        self.token.pack(side=LEFT)
  
        # DEVICE ID
        self.deviceidLabel = Label(self.quartoContainer,text="Device Id:", font=self.fontePadrao)
        self.deviceidLabel.pack(side=LEFT)
  
        self.deviceid = Entry(self.quartoContainer)
        self.deviceid["width"] = 30
        self.deviceid["font"] = self.fontePadrao
        self.deviceid.pack(side=LEFT)
  
        # TOPIC
        self.topicLabel = Label(self.quintoContainer,text="Topic:", font=self.fontePadrao)
        self.topicLabel.pack(side=LEFT)

        self.topic = Entry(self.quintoContainer)
        self.topic["width"] = 30
        self.topic["font"] = self.fontePadrao
        self.topic.pack(side=LEFT)

        #PAYLOAD
        self.payloadLabel = Label(self.quintoContainer, text="Speed:", font=self.fontePadrao)
        self.payloadLabel.pack(side=LEFT)
  
        self.payload = Entry(self.quintoContainer)
        self.payload["width"] = 30
        self.payload["font"] = self.fontePadrao
        self.payload.pack(side=LEFT)

        # AUTH BUTTON 
        self.autenticar = Button(self.sextoContainer)
        print(self.autenticar['command'])
        self.autenticar["text"] = "Send"
        self.autenticar["font"] = ("Arial", "8", "bold")
        self.autenticar["width"] = 12
        self.autenticar["command"] = self.verificaPub
        self.autenticar.pack()

        # HELP BUTTON   
        self.helps = Button(self.sextoContainer)
      #  print(self.helps['command'])
        self.helps["text"] = "Help"
        self.helps["font"] = ("Arial", "8", "bold")
        self.helps["width"] = 12
        self.helps["command"] = self.ajuda
        self.helps.pack()
  
        self.mensagem = Label(self.sextoContainer, text="", font=self.fontePadrao)
        self.mensagem.pack()

        self.ajuda = Label(self.sextoContainer, text="", font=self.fontePadrao)
        self.ajuda.pack()
  
    # Metodo verificar payload
    def verificaPub(self):
      host = self.host.get()
      port = self.port.get()
      token = self.token.get()
      deviceid = self.deviceid.get()
      payload = self.payload.get()
      topic = self.topic.get()

      url = "http://{}:{}/device/{}/actuate".format(host,port,deviceid)
      Token = "Bearer {}".format(token)

      headers = {
        'Authorization':Token,
        'Content-Type':'application/json'	
      }

      data = json.dumps( { "attrs": { topic: float(payload)}})

      response = requests.put(url, headers=headers, data=data)

    def ajuda(self):
      
      self.ajuda["text"] = """Host: Dojot IP     Port: 8000
                            Token: device-generated token
                            Device Id: device-generated Device ID 
                            Topic: pubTimer -> speed publishing on Dojot
                            pubMove -> conveyor speed
                            Speed: time in seconds"""
  
root = Tk()
GUI(root)
root.mainloop()
