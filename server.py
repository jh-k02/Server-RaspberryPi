import socketserver
import threading
import RPi.GPIO as GPIO
import time

HOST = ''
PORT = 7000
lock = threading.Lock() # syncronized thread created

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT) # GREEN LED
GPIO.setup(20, GPIO.OUT) # YELLOW LED
GPIO.setup(16, GPIO.OUT) # BLUE LED
GPIO.setup(12, GPIO.OUT) # PINK LED

pwm1 = GPIO.PWM(21, 5000)
pwm2 = GPIO.PWM(20, 5000)
pwm3 = GPIO.PWM(16, 5000)
pwm4 = GPIO.PWM(12, 5000)

greenPwm = 10
yellowPwm = 10
bluePwm = 10
pinkPwm = 10

class UserManager:
    def __init__(self):
        self.users = {}
        
    def addUser(self, username, conn, addr):
        if username in self.users:
            conn.send('The user is already registered.\n'.encode())
            return None
        
        lock.acquire()
        self.users[username] = (conn, addr)
        lock.release()
        
        self.sendMessageToAll('[%s] has entered.' %username)
        
        return username
    
    def removeUser(self, username):
        if username not in self.users:
            return
        
        lock.acquire()
        del self.users[username]
        lock.release()
        
        self.sendMessageToAll('[%s] has left.' %username)
        
    def messageHandler(self, username, msg):
        
        if msg[0] != '/':
         #   self.sendMessageToAll('[%s] %s' %(username, msg))
             
            global greenPwm
            global yellowPwm
            global bluePwm
            global pinkPwm
            if msg == 'GPIO Clear':
                pwm1.stop()
                pwm2.stop()
                pwm3.stop()
                pwm4.stop()
                GPIO.cleanup()
                
            if msg == 'GPIO Set':
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(21, GPIO.OUT)
                GPIO.setup(20, GPIO.OUT)
                GPIO.setup(16, GPIO.OUT)
                GPIO.setup(12, GPIO.OUT)
                
            if msg == 'GREEN LED ON':
                pwm1.start(greenPwm)
            
            if msg == 'GREEN LED OFF':
                pwm1.stop()
                greenPwm = 10
                
            if msg == 'GREEN LED UP':
                greenPwm = greenPwm + 10
                pwm1.ChangeDutyCycle(greenPwm)
                
            if msg == 'GREEN LED DOWN':
                greenPwm = greenPwm - 10
                pwm1.ChangeDutyCycle(greenPwm)
                
            if msg == 'YELLOW LED ON':
                pwm2.start(yellowPwm)
            
            if msg == 'YELLOW LED OFF':
                pwm2.stop()
                yellowPwm = 10
            
            if msg == 'YELLOW LED UP':
                yellowPwm = yellowPwm + 10
                pwm2.ChangeDutyCycle(yellowPwm)
                
            if msg == 'YELLOW LED DOWN':
                yellowPwm = yellowPwm - 10
                pwm2.ChangeDutyCycle(yellowPwm)
                
            if msg == 'BLUE LED ON':
                pwm3.start(bluePwm)
            
            if msg == 'BLUE LED OFF':
                pwm3.stop()
                bluePwm = 10
                
            if msg == 'BLUE LED UP':
                bluePwm = bluePwm + 10
                pwm3.ChangeDutyCycle(bluePwm)
                
            if msg == 'BLUE LED DOWN':
                bluePwm = bluePwm - 10
                pwm3.ChangeDutyCycle(bluePwm)
                
            if msg == 'PINK LED ON':
                pwm4.start(pinkPwm)
            
            if msg == 'PINK LED OFF':
                pwm4.stop()
                pinkPwm = 10
                
            if msg == 'PINK LED UP':
                pinkPwm = pinkPwm + 10
                pwm4.ChangeDutyCycle(pinkPwm)
                
            if msg == 'PINK LED DOWN':
                pinkPwm = pinkPwm - 10
                pwm4.ChangeDutyCycle(pinkPwm)
                
            self.sendMessageToAll('[%s]' %username)
            self.sendMessageToAll(msg)
      
            return
        
        if msg.strip() == '/quit':
            self.removeUser(username)
            return -1
    
    def sendMessageToAll(self, msg):
        for conn, addr in self.users.values():
            conn.send(msg.encode())
            
class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()
    
    def handle(self):
        print('[%s] connected' %self.client_address[0])
        
        try:
            username = self.registerUsername()
            msg = self.request.recv(1024)
            while msg:
                print('[%s] %s' %(username, msg.decode()))
                if self.userman.messageHandler(username, msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)
        
        except Exception as e:
            print(e)
            
        print('[%s] disconnected' %self.client_address[0])
        self.userman.removeUser(username)
        
    def registerUsername(self):
        while(True):
            username = self.request.recv(1024)
            username = username.decode().strip()
            if self.userman.addUser(username, self.request, self.client_address):
                return username
            
class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
    
def runServer():
    print('start server')
    
    try:
        server = ChatingServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()
    
    except KeyboardInterrupt:
        print('Shut down the server.')
        server.shutdown()
        server.server_close()
        
runServer()
