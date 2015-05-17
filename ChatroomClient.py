from PodSixNet.Connection import connection
from PodSixNet.Connection import ConnectionListener
import thread
from time import sleep
import sys
from Constants import Constants

silence = []
admin = False
firstTime = True

class MyNetworkListener(ConnectionListener):

    def Network(self, data):
        if not data["action"] in ignoreActions:
            print 'network data:', data
        pass

    def Network_connected(self, data):
        print "connected to the server"

    def Network_error(self, data):
        print "error:", data['error'][1]
        sleep(2)
        sys.exit()

    def Network_disconnected(self, data):
        print "disconnected from the server"
        sleep(2)
        sys.exit()
        
    def Network_post(self, data):
        u = data["username"].lower()
        if not u in silence:
            print data["username"] + " : " + data["message"]
        
    def Network_hug(self, data):
        print "You have been hugged by " + data["from"]
        
    def Network_userList(self, data):
        global isListing
        global userList
        global firstTime
        tempUsers = data["message"]
        if isListing:
            if len(tempUsers) == 1:
                print "There is currently one person on this server:"
            else:
                print "There are currently " + str(len(tempUsers)) + " people on this server:" 
            for i in tempUsers:
                print i
            isListing = False
        else:
            userList = data["message"]
        if firstTime:
            firstTime = False
            
               
            
    def Network_adminAccept(self, data):
        global admin
        if data["accepted"]:
            admin = True
            print "HELP : You are now an Admin!"
        else:
            print "HELP : Incorrect password"
        
    def Network_newUsername(self, data):
        global username
        print "New username : " + data["username"]
        username = data["username"]
        
        
        
        
def hug(user):
    print "Hugging user " + user
    networkListener.Send({"action":"hug","to":user,"from":username})
    
def silenceUser(user):
    silence.append(user.lower())
    print silence
    print "User " + user + " has been silenced"

def unsilenceUser(user):
    u = user.lower()
    global silence
    if u in silence:
        index = silence.index(user.lower())
        silence = silence[:index] + silence[index+1:]
    else:
        print "HELP : " + user + " is not silenced"
    
def list():
    global isListing
    networkListener.Send({"action":"getusers","username":username})
    isListing = True
    
def askAdminPassword(password):
    networkListener.Send({"action":"passwordRequest","username":username,"message":password})
    
def newUsername(newUsername):
    global username
    if usernameCheck(newUsername):
        networkListener.Send({"action":"changeUsername","newUsername":newUsername,"oldUsername":username})
    else:
        print "HELP : " + newUsername + " is an invalid username."
        
def adminStatus():
    if admin:
        print "HELP : You are an Admin."
    else:
        print "HELP : You are not an Admin."
    
def commandManager(input):
    global commands
    global commandNames
    global exitTimer
    if input[0] == "/":
        # These commands don't take any arguments
        
        if input == "/exit":
            networkListener.Send({"action":"exit","username":username})
            print "Exiting..."
            exitTimer = 10
        elif input == "/list":
            list()
            
        else: #Split the word to get the args
            words = input.split(" ")
            """
            word = ""
            for i in input:
                if i == " ":
                    words.append(word)
                    word = ""
                else:
                    word = word + i
            words.append(word)
            """
            # All these commands take in 1+ arguments
            
            if words[0] == "/n":
                if len(words) == 2:
                    if words[1] == "":
                        print
                    else:
                        try:
                            for i in range(0,int(words[1])):
                                print
                        except:
                            print "HELP : Please enter a valid number"
                else:
                    print
            
            elif words[0] == "/hug":
                if len(words) >= 2:
                    hug(words[1])
                else:
                    print "HELP : /hug requires two arguments. You had " + str(len(words)) + " argument(s)."
            elif words[0] == "/silence":
                if len(words) >= 2:
                    silenceUser(words[1])
                else:
                    print "HELP : /silence requires two arguments. You had " + str(len(words)) + " argument(s)."
            elif words[0] == "/desilence":
                if len(words) >= 2:
                    unsilenceUser(words[1])
                else:
                    print "HELP : /desilence requires two arguments. You had " + str(len(words)) + " argument(s)."
                    
            elif words[0] == "/username":
                if admin:
                    if len(words) == 2:
                        newUsername(words[1])
                    else:
                        print "HELP : /username requires two arguments. You had " + str(len(words)) + " argument(s)."
                else:
                    print "HELP : You do not have permission to that command."
                    
            elif words[0] == "/help":
                if len(words) == 2:
                    print "HELP : " + commands[str(words[1])]
                else:
                    print "There are " + str(len(commandNames)) + " commands currently:"
                    for i in commandNames:
                        print "/" + i + " : " + commands[i]
                    
            elif words[0] == "/admin":
                if len(words) >= 2:
                    if words[1] == "join":
                        if len(words) >= 3:
                            askAdminPassword(words[2])
                        else:
                            print "HELP : /admin join requires a password."
                    elif words[1] == "give":
                        if len(words) >= 3:
                            #giveAdmin(words[3])
                            pass
                        else:
                            print "HELP : /admin give requires a username to give admin status"
                    elif words[1] == "status":
                        adminStatus()
                else:
                    print commands["admin"]
                        
            else:
                print "HELP : Command " + input + " not found. type /help for more help"
                
        return False
    else:
        return True
        
def stopRunning():
    run = False
        
def inputer(input):
    tempInput = raw_input()
    input.append(tempInput)
        
def usernameCheck(testingUsername):
    global userList
    if not len(testingUsername.split(" ")) == 1:
        return False
    if testingUsername in userList:
        return False
    return True
        
def loop():
    global run
    global exitTimer
    input = []
    i = 0
    thread.start_new_thread(inputer, (input,))
    while run:
        networkListener.Pump()
        connection.Pump()
        if input:
            message = input[0]
            canProceed = commandManager(message)
            if canProceed:
                networkListener.Send({"action":"post","username":username,"message":str(message)})
                input = []
                message = None
            loop()
        if i == 10:
            networkListener.Send({"action":"getusers","username":username})
            i = 0
        else:
            i += 1
        
        if exitTimer > 0:
            exitTimer -= 1
        elif exitTimer == 0:
            run = False
        sleep(0.05)
        
#Start of the program
userList = []
ignoreActions = ["post","hug","userList","connected","adminAccept","newUsername"]
isListing = False
usernameTest = False
exitTimer = -1

commands = {
"silence":"Usage: /silence [username] - Used if you want to block people's messages",
"desilence":"Usage: /desilence [username] - Used if you want to unblock people's messages",
"hug":"Usage: /hug [username] - Used to hug people :)",
"admin":"Usage: /admin [join, give, status] ... - Used to give or get admin permission",
"username":"Usage: [ADMIN ONLY] /username [New Username] - Used to change your username",
"help":"Usage: /help OR /help [command] - Used if you want to find out more about something",
"/n":"Usage: /n {x} - Used to make {x} new line(s) NOTE: do /n to create one new line",
"exit":"Usage: /exit - Used to exit the chat",
"list":"Usage: /list - Used to list everyone in the chat"
}

commandNames = ["silence","desilence","hug","admin","username","help","/n","exit","list"]

address=raw_input("Address of Server (67.161.127.21:8000): ")
if not address:
    host, port= Constants.SERVER_EXTERNAL_ADDRESS, Constants.SERVER_PORT
else:
    host, port=address.split(":")
    
print host, port
        
print "Connecting to server on host: %s, port:%s" % (host, int(port))
networkListener = MyNetworkListener()
try:
  networkListener.Connect((host, int(port)))
except:
  print "Error connecting to server"
  sleep(3)
  exit()
  
networkListener.Send({"action":"firstGetUsers","message":"Hi"})

count = 0

"""
while userList == []:
    sleep(0.1)
    count += 1
    print count
"""
    
print userList
  
username = " "

while firstTime:
    networkListener.Pump()
    connection.Pump()
    sleep(0.05)

while username == " ": 
    tempUsername = raw_input("What is your username: ")
    if usernameCheck(tempUsername):
        username = tempUsername
    else:
        print "Please enter a valid username."

networkListener.Send({"action":"username","message":str(username)})
run = True
print "Starting loop"
loop()