import socket
import threading
import mysql.connector
import random
import json
from mysql.connector import Error
import time
import hashlib

class Room:
    def __init__(self):
        self.listOfClients = []
        self.listOfQuest = self.choose10questionsInRoom()

    def is_empty(self):
        if(len(self.listOfClients)==0):
            return True
        else:
            return False

    def is_full(self):
        if(len(self.listOfClients) == 3):
            return True
        else:
            return False

    def addToRoom(self, player):
        if(not self.is_full()):
            self.listOfClients.append(player)

    def choose10questionsInRoom(self):
        lst = []
        for i in range(10):
            quest, answer = random.choice(list(json_dict['quiz'].items()))
            while quest in lst:
                quest, answer = random.choice(list(json_dict['quiz'].items()))
            lst.append(quest)
        return lst


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients = []  #players who are click "play game"
    #loggedInUsersOnline = {} #players who are loggend in
    cls=[] #players who are online and who are not started the game
    listOfRooms = []

    def __init__(self):
        self.sock.bind(('localhost', 8888))
        self.sock.listen()
        print("I am waiting for connections...")
        room1 = Room()
        self.listOfRooms.append(room1)

    def run(self):

        while True:
            c, a = self.sock.accept()
            name = "guest" + str(random.randint(0, 1000))
            c.send(name.encode())
            print(name)
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()

    def handler(self, c, a):
        try:
            self.cls.append(c)
            soba = Room()
            print("Number of online clients: " + str(len(self.cls)))
            username=''
            print("This is server.. I am waiting for client decision")
            while(True):
                decision = c.recv(1024).decode()
                if(decision == "quit"):
                    print("User is quit the game")
                    break
                if(decision=="stop"):
                    print("User stopped chat")
                    c.send("stop".encode())
                    continue

                if(decision=="ranglist"):
                    print("Send rang list to user")
                    data = self.retrieveRangList()
                    c.send(data.encode())
                    continue
                if(decision.startswith('msg:')):
                    print("mora da je poruka od klijenta u chatu...")
                    print(decision)
                    self.broadcastMessage(c, decision)
                    print("posle broadcasta")
                    continue
                elif(int(decision) == -1):
                    print("User is quit the game")
                    break
                elif(int(decision) == 1):
                    print("User is logging...")
                    username = self.processingLogin(c, a)
                    if username==False:
                        break
                elif(int(decision) == 2):
                    print("User is registering")
                    self.processingRegister(c, a)
                elif(int(decision)== 0):
                    self.clients.append(c)
                    self.cls.remove(c)
                    if(self.areAllRoomsFull()):
                        room = Room()
                        self.listOfRooms.append(room)
                        self.listOfRooms[len(self.listOfRooms)-1].addToRoom(c)
                    else:
                        for room in self.listOfRooms:
                            if(not room.is_full()):
                                room.addToRoom(c)
                                print("Smesten u sobu")
                                break
                    print("Number of rooms: " + str(len(self.listOfRooms)))
                    print("Number of clients who wait for game: " + str(len(self.clients)))
                    print(c)

                    myRoom = self.findRoomOfCurrentPlayer(c)

                    print("Broj igraca za datu sobu: " + str(len(myRoom.listOfClients)))

                    while (len(myRoom.listOfClients)<3):
                        pass

                    print("Starting the game...")

                    score = self.sendQuestions(c, self.listOfRooms[len(self.listOfRooms)-1])
                    if(username!=''):
                        print("Nakon igre sledi azuriranje baze...")
                        print(username)
                        print(score)
                        self.importScoreInDatabase(username, score)

        except ConnectionResetError:
            print("Klijent se odjavio")
            #self.clients.remove(c)
            self.cls.remove(c)
        except ValueError:
            print("Greska bila sa primanjem poruke od klijenta")
            #self.clients.remove(c)
            self.cls.remove(c)

    def findRoomOfCurrentPlayer(self, c):
        for room in self.listOfRooms:
            for player in room.listOfClients:
                if(player == c):
                    return room
        return None

    def sendQuestions(self, c, room):
        score = 0
        for i in range(10):
            #forSending = self.listOfQuestions[i] + "///" + self.listOfAnswers[i][0] + "///" + self.listOfAnswers[i][1] + "///" + self.listOfAnswers[i][2] + "///" + self.listOfAnswers[i][3] + "///" + str(score)
            forSending = str(i+1) + ".  " + json_dict['quiz'][room.listOfQuest[i]]['question'] + "///" + json_dict['quiz'][room.listOfQuest[i]]['options'][0] + "///" + json_dict['quiz'][room.listOfQuest[i]]['options'][1] + "///" + json_dict['quiz'][room.listOfQuest[i]]['options'][2] + "///" + json_dict['quiz'][room.listOfQuest[i]]['options'][3] + "///" + str(score)
            print(forSending)
            c.send(forSending.encode())
            answer=c.recv(1024).decode()

            if(answer == "timeend"):
                print("Vreme je proteklo")
                break
            if(answer == "quit"):
                break
            if (answer == "helpmehint"):
                print("trazena pomoc hint")
                hint = json_dict['quiz'][room.listOfQuest[i]]['hint']
                hintForSending = "helpmehint///" + hint
                c.send(hintForSending.encode())
                answer = c.recv(1024).decode()
            if(answer == "helpmehalfhalf"):
                print("trazena pomoc half half")
                data='helpmehalfhalf///'
                counter=0
                while counter<2:
                    rand_num = random.randint(0,3)
                    if(json_dict['quiz'][room.listOfQuest[i]]['options'][rand_num] != json_dict['quiz'][room.listOfQuest[i]]['answer']):
                        data+=json_dict['quiz'][room.listOfQuest[i]]['options'][rand_num] + "///"
                        counter+=1
                print(data)

                c.send(data.encode())
                answer = c.recv(1024).decode()
            print("answer: " + answer)
            if (answer == "helpmehint"):
                print("trazena pomoc hint")
                hint = json_dict['quiz'][room.listOfQuest[i]]['hint']
                hintForSending = "helpmehint///" + hint
                c.send(hintForSending.encode())
                answer = c.recv(1024).decode()

            if(json_dict['quiz'][room.listOfQuest[i]]['answer'] == answer):
                print("Tacan odgovor")
                score+=1

            else:
                print("Netacan odgovor")
        return score

    def areAllRoomsFull(self):
        answer = True
        for room in self.listOfRooms:
            if(not room.is_full()):
                return False
        return answer

    def broadcastMessage(self, c, message):
        for client in self.cls:
            if(client != c):
                client.send(message.encode())
                print("poslata poruka klijentu koji nije posiljalac ove poruke")


    def processingLogin(self, c, a):
        user_pass = c.recv(1024).decode()
        username = user_pass.split('///')[0]
        password = user_pass.split('///')[1]
        print("{}    {}".format(username, password))

        counter = self.checkingUserFromDatabase(username, password)
        if(counter ==0):
            c.send("0".encode())
            return False
        elif(counter == 1):
            c.send("1".encode())
            self.isLoggedIn = 1
            print("Just logged in")
            return username

    def checkingUserFromDatabase(self, user, password):
        con = mysql.connector.connect(host='localhost', database='sakila', user='root', password='dusanruzic96.')

        pw = self.hashPassword(password)
        cur = con.cursor()
        cur.execute("SELECT * FROM korisnici WHERE username LIKE '{}' AND password LIKE '{}'".format(user, pw))
        rows = cur.fetchall()

        if(len(rows) == 0):
            print("Ne postoji")
            con.close()
            return 0
        else:
            print("Taj user postoji")
            con.close()
            return 1

    def retrieveRangList(self):
        con = mysql.connector.connect(host='localhost', database='sakila', user='root', password='dusanruzic96.')
        cur = con.cursor()
        cur.execute("SELECT * FROM korisnici ORDER BY score DESC")
        rows = cur.fetchall()
        data=""
        for row in rows:
            data += row[1] + "/-/" + str(row[6]) + "///"

        print (data)
        con.close()
        return data

    def processingRegister(self, c, a):
        print("I am waiting for username to check if it exists in database:")

        userData = c.recv(1024).decode()

        username= userData.split('///')[0]
        firstName = userData.split('///')[1]
        lastName = userData.split('///')[2]
        email = userData.split('///')[3]
        password = userData.split('///')[4]
        if(self.checkingUsernameFromDatabase(username) == 0):
            c.send("0".encode())
            print("That username exists... Trying again...")
        else:
            c.send("1".encode())
            print("That username doesn't exists...Super")
            self.importingUserInDatabase(username, firstName, lastName, password, email)
            print("Successfully added user")
            self.isRegister = True
            print("Sending message: Please check your email for validation")
            print("Just registered")

    def importingUserInDatabase(self, user, first, last,  passw, mail):
        con = mysql.connector.connect(host='localhost', database='sakila', user='root', password='dusanruzic96.')

        pw = self.hashPassword(passw)

        query = "INSERT INTO korisnici(username, firstname, lastname, password, email) VALUES (%s, %s, %s, %s, %s) "
        args = (user, first, last, pw, mail)

        try:

            cursor = con.cursor()
            cursor.execute(query, args)

            con.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            con.close()

    def hashPassword(self, txt):
        hash = hashlib.md5(txt.encode())
        return hash.hexdigest()

    def checkingUsernameFromDatabase(self, user):
        con = mysql.connector.connect(host='localhost', database='sakila', user='root', password='dusanruzic96.')

        cur = con.cursor()
        cur.execute("SELECT * FROM korisnici WHERE username LIKE '{}'".format(user))

        rows = cur.fetchall()
        con.close()
        if(len(rows) == 0):
            print("That username is available")
            return 1
        else:
            print("That username is not available.")
            return 0

    def enterTheRoom(self, c, a):
        pass

    def importScoreInDatabase(self, username, scor):
        con = mysql.connector.connect(host='localhost', database='sakila', user='root', password='dusanruzic96.')

        query = "UPDATE korisnici SET score=score+%s WHERE username LIKE %s"
        args = (scor, username)

        try:

            cursor = con.cursor()
            cursor.execute(query, args)

            con.commit()
        except Error as error:
            print(error)

        finally:
            cursor.close()
            con.close()
        
        print("Successfull added score")



with open("pitanja.json") as f:
    json_example = f.read()

json_dict = json.loads(json_example)
#print(json_dict)


server = Server()
server.retrieveRangList()
server.run()


