from Tkinter import *
import SocketServer
import threading
from walldriver import PANEL_NUM


#w.create_line(0, 0, 200, 100)
#w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
#w.create_rectangle(50, 25, 150, 75, fill="blue")


		

WALL_LAYOUT = (
(None,0,4,8,12,16,20,24,28,None),
(None,1,5,9,13,17,21,25,29,None),
(32,  2,6,10,14,18,22,26,30,34),
(33,  3,7,11,15,19,23,27,31,35)
)



class WallSimulator(object):
	
	class Channel(object):
		def __init__(self,panel,channel_num):
			self._value = 0
			self.panel = panel
			self.channel_number = channel_num
		
		def _set_val(self,val):
			self._value =val
			Tk().generate_event('<<Channel-Update-%s>>' % channel_num)
		def _get_val(self):
			return self._value
		value = property(fget=_get_val,fset=_set_val)
			
			
	class Panel(object):
		def __init__(self,canvas,rect,panel_num):
			self.canvas = canvas
			self.rect = rect
			self.r = WallSimulator.Channel(self,panel_num*3+1)
			self.g = WallSimulator.Channel(self,panel_num*3+2)
			self.b = WallSimulator.Channel(self,panel_num*3+3)
			
		def _update(self):
			canvas.itemconfig(self.rect,fill='#%0.2X%0.2X%0.2X' % (self.r.value,self.g.value,self.b.value))


			
	
	
	def __init__(self):
		
		# Setup TCP server
		self.host = "localhost"
		self.port = 5005
		self.server = WallSimulator.WallTCPServer((self.host,self.port), WallSimulator.WallTCPHandler, wall=self)
		#super(WallServer,self).__init__()
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		
		self.debug_thread = threading.Thread(target=mainloop)
		
		# Setup GUI
		self.master = Tk()
		self.w = Canvas(self.master, width=1000, height=400)
		self.w.pack()
		
		
		panel_w = 98
		panel_h = 98
		
		self.panels = {}
		self.channels = {}
		
		y = 1
		for row in WALL_LAYOUT:
			x = 1
			for panel_num in row:
				
				i = self.w.create_rectangle(x, y, panel_w, panel_h, fill='#000')
				
				if panel_num:
					p = WallSimulator.Panel(canvas=self.w, rect=i, panel_num=panel_num)
				
					self.panels[panel_num+1] = p
					
					j = panel_num*3+1
					self.channels[j] = p.r
					self.master.bind('<<Channel-Update-%s>>' % j, p._update)
					j = panel_num*3+2
					self.channels[j] = p.g
					self.master.bind('<<Channel-Update-%s>>' % j, p._update)
					j = panel_num*3+3
					self.channels[j] = p.b
					self.master.bind('<<Channel-Update-%s>>' % j, p._update)
				
				x += panel_w+2
			
			y += panel_h+2	


	def start(self):	
		#print "Starting server at %s:%s..." % (self.host,self.port)
		#self.server_thread.start()
		print "Starting GUI..."
		#self.mainloop()
		self.debug_thread.start()

	
	class WallTCPServer(SocketServer.TCPServer):
		def __init__(self,*args,**kwargs):
			self.wall = kwargs.pop('wall')
			SocketServer.TCPServer.__init__(self,*args,**kwargs)


	class WallTCPHandler(SocketServer.StreamRequestHandler):
		def handle(self):
			channel,value = self.rfile.readline().strip().split(' ')
			self.server.wall.channels[int(channel)] = int(value)
	
		
def main():
	w = WallSimulator()
	w.start()

if __name__ == '__main__':
	main()
