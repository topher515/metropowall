import SocketServer
import time

class WallRGBHandler(SocketServer.BaseRequestHandler):
	
	
	def handle(self):
		#print self.request
		
		data = ''
		buff = self.request.recv(4096).strip()
		while len(buff):
			data += buff
			buff = self.request.recv(4096).strip()
		
		#print "Got %s bytes of data from %s at %s" % (len(data),self.client_address[0], time.time())
		print data
		self.request.send('ok!')
		# socket.sendto(data.upper(), self.client_address)
		
		
def main():
	HOST, PORT = "localhost", 5005
	server = SocketServer.TCPServer((HOST,PORT), WallRGBHandler)
	print "Starting server..."
	server.serve_forever()


if __name__ == '__main__':
	main()
