from PodSixNet.Connection import connection
import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
from Constants import Constants
class ClientChannel(PodSixNet.Channel.Channel):

    def Network(self, data):
        #print data["message"]
        pass
        
    def Network_username(self, data):
        print "Creating User!"
        boxesServe.postToAll("SERVER", "User " + data["message"] + " has joined the server.")
        boxesServe.createUser(data["message"])
            
    def Network_post(self, data):
        tempUsername = data["username"]
        tempMessage = data["message"]
        boxesServe.postToAll(tempUsername, tempMessage)
        
    def Network_hug(self, data):
        boxesServe.slashHug(data["to"], data["from"])
        
    def Network_getusers(self, data):
        boxesServe.sendUsernames(data["username"])
        
    def Network_passwordRequest(self, data):
        boxesServe.passwordRequest(data["username"], data["message"])
        
    def Network_changeUsername(self, data):
        boxesServe.changeUsername(data["oldUsername"], data["newUsername"])
        
    def Network_firstGetUsers(self, data):
        boxesServe.firstSendUsernames()
        
    def Network_exit(self, data):
        boxesServe.exit(data)
        
class User():
    def __init__(self, channel, addr, username):
        self.channel = channel
        self.address = addr
        self.username = username
    def getChannel(self):
        return self.channel
    def getUsername(self):
        return self.username
    def setUsername(self, newUsername):  
        self.username = newUsername

class BoxesServer(PodSixNet.Server.Server):
 
    channelClass = ClientChannel
 
    def Connected(self, channel, addr):
        self.channel1 = channel
        self.tempChannel = channel
        self.tempAddr = addr
        print self.tempChannel
        print 'new connection:', channel
        
    def sendCorrect(self):
        self.channel1.Send({"action":"message","message":"You are correct"})
        print "'You are correct' sent!"
        
    def createUser(self, username):
        user = User(self.tempChannel, self.tempAddr, username)
        users.append(user)
        
    def sendToAll(self, message):
        for i in users:
            channel = i.getChannel()
            channel.Send({"action":"newtext","message":message})
            
    def postToAll(self, username, message):
        for i in users:
            channel = i.getChannel()
            channel.Send({"action":"post","username":username,"message":message})
            
    def slashHug(self, toUsername, fromUsername):
        for i in users:
            if i.getUsername().lower() == toUsername.lower():
                channel = i.getChannel()
                channel.Send({"action":"hug","from":fromUsername})
                
    def findChannel(self, username):
        for i in users:
            if i.getUsername().lower() == username.lower():
                return i.getChannel()
                
    def findUser(self, username):
        for i in users:
            if i.getUsername().lower() == username.lower():
                return i
                
    def getUsernames(self):
        tempUsers = []
        for i in users:
            tempUsers.append(i.getUsername())
        return tempUsers
                
    def sendUsernames(self, toUsername):
        #Grab the channel:
        channel = self.findChannel(toUsername)
        usernames = self.getUsernames()
        channel.Send({"action":"userList","message":usernames})
        
    def passwordRequest(self, username, testPassword):
        channel = self.findChannel(username)
        if testPassword == password:
            channel.Send({"action":"adminAccept","accepted":True})
        else:
            channel.Send({"action":"adminAccept","accepted":False})
            
    def changeUsername(self, oldUsername, newUsername):
        user = self.findUser(oldUsername)
        user.setUsername(newUsername)
        user.getChannel().Send({"action":"newUsername","username":newUsername})
        
    def firstSendUsernames(self):
        usernames = self.getUsernames()
        self.tempChannel.Send({"action":"userList","message":usernames})
        
    def exit(self, data):
        global users
        username = data["username"]
        user = self.findUser(username)
        index = users.index(user)
        #print users
        users = users[:index] + users[index+1:]
        #print users
                
address=raw_input("Start the server on what address (192.168.1.144:8000): ")
if not address:
    host, port=Constants.SERVER_INTERNAL_ADDRESS, Constants.SERVER_PORT
else:
    host, port=address.split(":")
    
password = raw_input("Please supply a password for admins : ")
if not password:
    password = Constants.SERVER_DEFULT_PASSWORD
        
print "Starting server on host: %s, port:%s" % (host, int(port))
users = []
boxesServe=BoxesServer(localaddr=(host, int(port)))

while True:
    boxesServe.Pump()
    sleep(0.01)
