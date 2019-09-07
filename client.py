import tkinter
import socket
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import time

class Client(threading.Thread):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 8888

    def __init__(self):
        threading.Thread.__init__(self)
        self.state = 'guest'
        self.chatting = False
        self.end = False

        self.s.connect((self.host, self.port))

    def run(self):
        self.state = self.s.recv(1024).decode()
        print(self.state)

    def login(self):
        self.s.send("1".encode())
        print("LOGGING...")
        user_pass = name.get() +"///" + password.get()
        self.s.send(user_pass.encode())
        password.set("")
        returnedData = self.s.recv(1024).decode()
        print(returnedData)
        if(int(returnedData)==0):
            self.s.send("1".encode())
            showMsgBoxLogin()
            sys.exit()
        else:
            self.state = name.get()
            lblState['text'] = "User:" + name.get()
            name.set("")

    def register(self):
        self.s.send("2".encode())
        print("REGISTERING...")
        data = usernameRegistration.get() + "///" + firstName.get() + "///" + lastName.get() + "///" + email.get() + "///" + passwordRegistration.get()
        self.s.send(data.encode())
        usernameRegistration.set("")
        firstName.set("")
        lastName.set("")
        email.set("")
        passwordRegistration.set("")
        if(self.s.recv(1024).decode() == "0"):
            print('postoji taj username')
            showMsgBoxRegister()

    def enteringRoom(self):
        btnHelp1.configure(state='normal')
        btnHelp2.configure(state='normal')
        btnIgraj.configure(state='disabled')
        btnshowScores.configure(state='disabled')
        ABC2.destroy()
        self.s.send("0".encode())
        lblScore.configure(text='SCORE: 0')
        lblTimer.configure(text=str(timee))

        for i in range(10):
            thr=threading.Thread(target=self.receiveQuestions, args=(lblMainQuest, btnQuestionA, btnQuestionB, btnQuestionC, btnQuestionD))
            thr.daemon = True
            thr.start()


    def receiveQuestions(self, question, answerA, answerB, answerC, answerD):

        while True:

            received = self.s.recv(1024).decode()
            if(received.startswith('helpmehalfhalf///')):
                print(received)
                lst = received.split('///')[1:3]

                print(lst)
                firstWrong = lst[0]
                print(firstWrong)
                secondWrong = lst[1]
                print(secondWrong)
                print()
                print(btnQuestionA['text'])
                print(btnQuestionB['text'])
                print(btnQuestionC['text'])
                print(btnQuestionD['text'])
                if(btnQuestionA['text'] == firstWrong or btnQuestionA['text'] == secondWrong):
                    print("dobro")
                    btnQuestionA.configure(text='X', font=('arial', 14, 'bold'))

                if (btnQuestionB['text'] == firstWrong or btnQuestionB['text'] == secondWrong):
                    print("dobro")

                    btnQuestionB.configure(text='X', font=('arial', 14, 'bold'))

                if (btnQuestionC['text'] == firstWrong or btnQuestionC['text'] == secondWrong):
                    print("dobro")

                    btnQuestionC.configure(text='X', font=('arial', 14, 'bold'))

                if (btnQuestionD['text'] == firstWrong or btnQuestionD['text'] == secondWrong):
                    print("dobro")

                    btnQuestionD.configure(text='X', font=('arial', 14, 'bold'))

            elif(received.startswith('helpmehint///')):
                hint = received.split('///')[1]
                lblMainQuest['text']+="\nHINT: " + hint
                print(hint)
            else:
                countSeconds(float(lblTimer['text']))
                btnQuestionA.configure(state='normal')
                btnQuestionB.configure(state='normal')
                btnQuestionC.configure(state='normal')
                btnQuestionD.configure(state='normal')
                #print(received)
                chunks = received.split('///')
                question.configure(text=chunks[0])
                answerA.configure(text=chunks[1])
                answerB.configure(text=chunks[2])
                answerC.configure(text=chunks[3])
                answerD.configure(text=chunks[4])
                lblScore.configure(text="SCORE: " + chunks[5])
                break

    def sendBackAnswer(self, answer):
        threading.Thread(target=self.s.send(answer.encode()))
        if(lblMainQuest['text'][0]==str(1) and lblMainQuest['text'][1]==str(0)):
            client.end=True
            print("FINISHHH")

    def sendMessage(self, text):
        msg = "msg:" + self.state + ": " + text
        print(msg)
        self.s.send(msg.encode())
        message.set("")
        print("Poslat text: " + msg)
        txtChat.insert(INSERT, msg[4:] +'\n')

    def listeningForMessages(self):
        while self.chatting:
            receivedMessage = self.s.recv(1024).decode()
            if(receivedMessage.startswith('msg:')):
                print("primioo od nekog drugog klijenta")
                txtChat.insert(INSERT, receivedMessage[4:] + "\n")
        print("kraj chata, kraj while petlje")

    def startChat(self):
        txtMessage.focus()
        txtMessage.configure(state='normal')
        btnIgraj.configure(state='disabled')
        btnStartChat.configure(state='disabled')
        btnStopChat.configure(state='normal')
        txtUsername.configure(state='disabled')
        txtUsernameRegistration.configure(state='disabled')
        self.chatting = True
        print("starting chat...")
        thr = threading.Thread(target=self.listeningForMessages)
        thr.start()

    def stopChat(self):
        txtMessage.configure(state='disabled')
        btnIgraj.configure(state='normal')
        btnStopChat.configure(state='disabled')
        btnStartChat.configure(state='normal')
        txtUsername.configure(state='normal')
        txtUsernameRegistration.configure(state='normal')
        self.chatting=False
        print("stopping chat...")
        self.s.send('stop'.encode())
        print("posle send")

    def viewRangList(self):
        self.s.send("ranglist".encode())
        print("primanje rang liste")
        rangList = self.s.recv(2048).decode()
        self.show(rangList)

    def show(self, data):
        nizUsernameScore = data.split('///')
        nizUsernameScore.pop()
        print(nizUsernameScore)

        for i in table.get_children():
            table.delete(i)

        counter = 1

        for item in nizUsernameScore:
            name = item.split('/-/')[0]
            score = item.split('/-/')[1]
            table.insert("", "end", values=(counter, name, score), tags=(name,))
            counter += 1
        table.tag_configure(client.state, background='red')

    def helpMe1(self):
        print("trazim pomoc pola pola...")
        self
        self.s.send("helpmehalfhalf".encode())
        btnHelp1.configure(state='disabled', bg='black')

    def helpMe2(self):
        print("trazim hint")
        self.s.send("helpmehint".encode())
        btnHelp2.configure(state='disabled', bg='black')



root = Tk()
root.title("Multiplayer online quizz")

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        sys.exit()

def showMsgBoxLogin():
    messagebox.showwarning("LOGIN DENNIED!!!", "You username-password pair doesn't exist. Please re-open game and try again.")

def showMsgBoxRegister():
    messagebox.showinfo("REGISTER DENNIED!!!", "It already exist user with that username")

def blockingLogin(a,b,c):
    if(name.get()!="" and password.get()!=""):
        btnLogin.configure(state='normal')
    else:
        btnLogin.configure(state='disabled')

def blockingRegister(a,b,c):
    if(usernameRegistration.get()!= "" and firstName.get()!="" and lastName.get()!="" and email.get()!="" and passwordRegistration.get()!="" and "@" in email.get()):
        btnRegistration.configure(state='normal')
    else:
        btnRegistration.configure(state='disabled')

def blockingSendingMessage(a,b,c):
    if message.get()=="":
        btnSend.configure(state='disabled')
    else:
        btnSend.configure(state='normal')

def setDateAndTime():
    lblDateAndTime.configure(text=time.asctime())
    root.after(1000, lambda: setDateAndTime())

def countSeconds(counter):
    lblTimer.configure(text=str(round(counter,1)))
    if(counter<0.1 or client.end):
        btnQuestionA.destroy()
        btnQuestionB.destroy()
        btnQuestionC.destroy()
        btnQuestionD.destroy()
        lblQuestionA.destroy()
        lblQuestionB.destroy()
        lblQuestionC.destroy()
        lblQuestionD.destroy()
        lblMainQuest.destroy()
        if(counter<0.01):
            client.s.send("timeend".encode())

            lblnovi = Label(ABC1c, font=('arial', 20, 'bold'),text='TIME IS COUNT DOWN. \nQUIZZ IS FINISHED.\nYOUR ' + lblScore['text'] + '/10', bg='gray12', fg='red', bd=1, width=30, height=7,
                              justify=CENTER)
        else:
            btnshowScores.configure(state='normal')
            lblnovi = Label(ABC1c, font=('arial', 20, 'bold'),
                            text='QUIZZ IS FINISHED.\nYOUR ' + lblScore['text'] + '/10' + '.\nELAPSED TIME: ' + str(round(timee - float(lblTimer['text']),2)), bg='gray12', fg='white', bd=1, width=30, height=7,
                            justify=CENTER)
        lblnovi.grid(row=0, column=0, pady=4)
        return
    counter = counter - 0.1
    root.after(100, lambda : countSeconds(counter))

client = Client()
client.run()


root.geometry('1920x1080')
root.configure(bg='gray12')

tabControl = ttk.Notebook(root)
tab1 = Frame(tabControl)
tabControl.add(tab1, text='Game')
tab2 = Frame(tabControl)
tabControl.add(tab2, text='Rang List')

tabControl.pack()
#============RANG LISTA =============
lblRangList = Label(tab2, bg='red', text="High Scores", font=("Helvetica",40))
lblRangList.grid(row=0, columnspan=3, sticky='we')
cols = ('Position', 'Name', 'Score')
table = ttk.Treeview(tab2, columns=cols, show='headings', height='20')
for col in cols:
    table.heading(col, text=col)
table.grid(row=1, column=0, columnspan=2)

btnshowScores = Button(tab2, text="Show scores", width=15, command = lambda: client.viewRangList())
btnshowScores.grid(row=4, column=0)
#============KRAJ====================

#============PRVI PROZOR = GAME =================
ABC = Frame(tab1, bg='gray12')
ABC.grid(row=0, column=0)

ABC1 = Frame(tab1, bg='gray12')
ABC1.grid(row=0, column=0)
ABC2 = Frame(tab1, bg='gray12')
ABC2.grid(row=0, column=1)

ABC1a = Frame(ABC1, bg='gray20')
ABC1a.grid(row=0, column=0, pady=30)
ABC1b = Frame(ABC1, bg='gray12')
ABC1b.grid(row=1, column=0)
ABC1c = Frame(ABC1, bg='gray26')
ABC1c.grid(row=2, column=0, pady=30)


#=================USER: ime ===============
lblState = Label(ABC1a, text="User: " + client.state,font=('arial',14,'bold'), width=30, bg="gray26", fg="firebrick1")
lblState.grid(row=0, column=0)
lblDateAndTime = Label(ABC1a, text=time.asctime(), width=40)
lblDateAndTime.grid(row=0, column=1)

btnIgraj = Button(ABC1a, text='Play game',font=('arial',14,'bold'), bg="gold3", fg="white",border='10', relief=GROOVE, command= lambda: client.enteringRoom())
btnIgraj.grid(row=1,column=0,columnspan=2, sticky='we')
#btnIgrajPonovo = Button(ABC1a, text='Play again', command= lambda: client.enteringRoom())
#btnIgrajPonovo.grid(row=1,column=1)
lblScore = Label(ABC1a, text="", font=('arial',14), bg='gray20', fg='gold3')
lblScore.grid(row=2, column=0, pady=10)
timee = 40
lblTimer = Label(ABC1a, text='',font=('arial',20, 'bold'), bg='gray20', fg='red')
lblTimer.grid(row=2, column=1)
#===================ACTIVATE DATE AND TIME LABEL======================
setDateAndTime()
#=====================================================================
logoImage = PhotoImage(file='logo33.png')
btnHelp1 = Button(ABC1b, image=logoImage, bg='gray50', height=70, state='disabled', command=client.helpMe1)
btnHelp1.grid(row=1, column=0, padx=20)

btnHelp2 = Button(ABC1b, image=logoImage, bg='gray50', height=70, state='disabled', command=client.helpMe2)
btnHelp2.grid(row=1, column=1, padx=150)



#===============PITANJE===============
lblMainQuest = Label(ABC1c, font=('helvetica', 14, 'bold', 'italic'), height=6, bg='gray12', text='', fg='white', bd=5, width=50, justify=CENTER)
lblMainQuest.grid(row=0, column=0, columnspan=4,pady=4)

#==============================BUTTONS A,B,C,D=======================
lblQuestionA = Label(ABC1c, font=('helvetica', 14, 'bold'), text='A', bg='gray15', fg='light sea green', bd=5, justify=CENTER)
lblQuestionA.grid(row=1, column=0, pady=4, sticky=E)

btnQuestionA = Button(ABC1c, font=('helvetica', 14, 'bold'), bg='gray15', fg='white', bd=1, width=17, height=3, justify=CENTER, state='disabled', command= lambda: client.sendBackAnswer(btnQuestionA['text']))
btnQuestionA.grid(row=1, column=1, pady=4)

lblQuestionB = Label(ABC1c, font=('helvetica', 14, 'bold'), text='B', bg='gray15', fg='light sea green', bd=5, justify=LEFT)
lblQuestionB.grid(row=1, column=2, pady=4, sticky=E)

btnQuestionB = Button(ABC1c, font=('helvetica', 14, 'bold'), bg='gray15', fg='white', bd=1, width=17, height=3, justify=CENTER, state='disabled', command= lambda: client.sendBackAnswer(btnQuestionB['text']))
btnQuestionB.grid(row=1, column=3, pady=4)

lblQuestionC = Label(ABC1c, font=('helvetica', 14, 'bold'), text='C', bg='gray15', fg='light sea green', bd=5, justify=CENTER)
lblQuestionC.grid(row=2, column=0, pady=4, sticky=E)

btnQuestionC = Button(ABC1c, font=('helvetica', 14, 'bold'), bg='gray15', fg='white', bd=1, width=17, height=3, justify=CENTER,state='disabled', command= lambda: client.sendBackAnswer(btnQuestionC['text']))
btnQuestionC.grid(row=2, column=1, pady=4)

lblQuestionD = Label(ABC1c, font=('helvetica', 14, 'bold'), text='D', bg='gray15', fg='light sea green', bd=5, justify=CENTER)
lblQuestionD.grid(row=2, column=2, pady=4, sticky=E)

btnQuestionD = Button(ABC1c, font=('helvetica', 14, 'bold'), bg='gray15', fg='white', bd=1, width=17, height=3, justify=CENTER,state='disabled', command= lambda: client.sendBackAnswer(btnQuestionD['text']))
btnQuestionD.grid(row=2, column=3, pady=4)


#============================Login and Register===========================================================
ABC2login = Frame(ABC2, bg='gray18', height=200)
ABC2login.grid(row=0, column=0, pady=15)

ABC2register = Frame(ABC2, bg='gray18', height=200)
ABC2register.grid(row=1, column=0, pady=15)

ABC2chat = Frame(ABC2, bg='gray26', height=200)
ABC2chat.grid(row=2, column=0, pady=15)


lblLogin = Label(ABC2login, font=('helvetica', 14, 'bold'), text="LOGIN", width=35, bg="gray26", fg="chartreuse2")
lblLogin.grid(row=0, column=0, columnspan=2)

lblUsername = Label(ABC2login, font=('helvetica', 11), text="Enter your username", width=15, bg="chartreuse2", fg="gray5")
lblUsername.grid(row=1, column=0, pady=4)
name=StringVar()
name.trace("w", blockingLogin)
txtUsername = Entry(ABC2login, font=('helvetica', 11), width=15, textvariable=name, bg="white")
txtUsername.grid(row=1, column=1)
lblPassword = Label(ABC2login, font=('helvetica', 11), text="Enter your password", width=15, bg="chartreuse2", fg="gray5")
lblPassword.grid(row=2, column=0, pady=4)
password=StringVar()
password.trace("w", blockingLogin)
txtPassword = Entry(ABC2login, font=('helvetica', 11), width=15, textvariable=password, show="*", bg="white")
txtPassword.grid(row=2, column=1)
btnLogin = Button(ABC2login, text="Click to login", fg="chartreuse2", width=20, state='disabled',border='5', relief=GROOVE, command= lambda: client.login(), bg="gray16")
btnLogin.grid(row=3, column=0, columnspan=2)



lblRegister = Label(ABC2register, font=('helvetica', 14, 'bold'), text="REGISTER", width=35, bg="gray26", fg="light sea green")
lblRegister.grid(row=0, column=0, columnspan=2)

lblUsernameRegistration = Label(ABC2register, text="Enter username:", font=('helvetica', 11), width=15, bg="light sea green", fg="gray5")
lblUsernameRegistration.grid(row=1, column=0, pady=4)
usernameRegistration=StringVar()
usernameRegistration.trace("w", blockingRegister)
txtUsernameRegistration = Entry(ABC2register, width=15,  bg="white", font=('helvetica', 11), textvariable=usernameRegistration)
txtUsernameRegistration.grid(row=1, column=1)

lblFirstName = Label(ABC2register, text="Enter your first name:", font=('helvetica', 11),width=15, bg="light sea green", fg="gray5")
lblFirstName.grid(row=2, column=0, pady=4)
firstName=StringVar()
firstName.trace("w", blockingRegister)
txtFirstName = Entry(ABC2register, width=15, font=('helvetica', 11),  bg="white",textvariable=firstName)
txtFirstName.grid(row=2, column=1)

lblLastName = Label(ABC2register, text="Enter your last name:", font=('helvetica', 11),  width=15, bg="light sea green", fg="gray5")
lblLastName.grid(row=3, column=0, pady=4)
lastName=StringVar()
lastName.trace("w", blockingRegister)
txtLastName = Entry(ABC2register, width=20, textvariable=lastName,  bg="white")
txtLastName.grid(row=3, column=1)

lblEmail = Label(ABC2register, text="Enter your e-mail:",  font=('helvetica', 11), width=15, bg="light sea green", fg="gray5")
lblEmail.grid(row=4, column=0, pady=4)
email=StringVar()
email.trace("w", blockingRegister)
txtEmail = Entry(ABC2register, width=20, textvariable=email,  bg="white")
txtEmail.grid(row=4, column=1)

lblPasswordRegistration = Label(ABC2register, text="Enter your password:", font=('helvetica', 11), width=15, bg="light sea green", fg="gray5")
lblPasswordRegistration.grid(row=5, column=0, pady=4)
passwordRegistration=StringVar()
passwordRegistration.trace("w", blockingRegister)
txtPasswordRegistration = Entry(ABC2register, width=20, textvariable=passwordRegistration, show="*",  bg="white")
txtPasswordRegistration.grid(row=5, column=1)

btnRegistration = Button(ABC2register, text="Click to register", width=20,fg="light sea green", bg="gray16",state='disabled',border='5', relief=RIDGE, command= lambda: client.register())
btnRegistration.grid(row=6, column=0, columnspan=2)

#================CHAT====================================
btnStartChat = Button(ABC2chat, text='START CHAT:', pady=2, bg="tomato",fg="white",border='5', relief=RIDGE, command= lambda: client.startChat())
btnStartChat.grid(row=0, column=0, sticky='w')
btnStopChat = Button(ABC2chat, text='STOP CHAT:', pady=2, bg="tomato",fg="white", state='disabled', border='5', relief=RIDGE, command= lambda: client.stopChat())
btnStopChat.grid(row=0, column=1, sticky='e')

txtChat = Text(ABC2chat, height=10, bg="gray18", fg="white")
txtChat.grid(row=1, column=0, columnspan=2)
message = StringVar()
txtMessage = Entry(ABC2chat, width=50, textvariable = message, state='disabled')
message.trace("w", blockingSendingMessage)
txtMessage.grid(row=2, column=0)
btnSend = Button(ABC2chat, text='Send message', state='disabled',border='6', relief=RAISED, command=lambda: client.sendMessage(message.get()))
btnSend.grid(row=2, column=1)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()






