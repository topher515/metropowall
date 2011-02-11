from sprites import Sprite, SpritePlane
from random import randint as rint
from walldriver import WallDriver, KeyboardHandler, PANEL_NUM



class SnakeScene(SpritePlane):
	
	
	def __init__(self,bg=(0,0,0),snake=(0,240,0),apple=(255,0,0),snake_max_len=4):
		
		
		super(SnakeScene,self).__init__(tempo=360,bg=bg)
		
		self.snake = Sprite(color=snake,blend=False,z=10,trail=snake_max_len)
		self.add_sprite(0,0,self.snake)
		
		self.apple_time = 0
		self.apple = Sprite(color=apple,blend=False,z=5)
		self.add_sprite(0,0,self.apple)
		
		self.snake_reset()
		self.apple_reset()
		
		self.points = 0
		
		self._snake_dir = rint(0,4) 
		
	
	def add_point(self):
		p = Sprite(color=(255,255,255),blend=False,z=0)
		self.add_sprite(*self.wall1d_to_plane2d(self.points),sprite=p)
		self.points +=1
		
	def apple_reset(self):	
		self.apple_time = 0
		self.move_to(self.apple,*self.random_visible_plane2d())
		
	def snake_reset(self):
		self.move_to(self.snake,*self.random_visible_plane2d())
		
	
	def up(self): self._snake_dir = 0
	def right(self): self._snake_dir = 1
	def down(self): self._snake_dir = 2
	def left(self): self._snake_dir = 3
	
	def _snake_step(self):
		
		if self.snake.loc() == self.apple.loc():
		#	self.snake_reset()
			self.apple_reset()
			self.add_point()
		
		r = self._snake_dir
		if r == 0:
			self.move_up(self.snake)
		elif r == 1:
			self.move_right(self.snake)
		elif r == 2:
			self.move_down(self.snake)
		else: # r == 3
			self.move_left(self.snake)
	
	
	def step(self,seconds):
		if not super(SnakeScene,self).step(seconds):
			return False
		#print 'step %s' % seconds	
			
		for i in xrange(int(self.beats())):
			self._snake_step()
			self.apple_time += 1
			if self.apple_time >= 10:
				self.apple_reset()
		
		return True
	
	def rgb(self,base_rgb=None):
		
		if self.points < 4:
			return super(SnakeScene,self).rgb()
		else:
			return [(rint(0,255),rint(0,255),rint(0,255)) for i in xrange(0,PANEL_NUM)]
		
		
def wall_test():
	
	print """
	SNAKE2 for METROPOWALL
	
	Arrow keys control. Press 'q' to exit.
	
	Collect all the apples to win a special surprise!
	
	"""
	
	wd = WallDriver(refresh=13,host='localhost',port=7778)
	
	k = KeyboardHandler()
	
	s = SnakeScene()
	
	k.register_arrows(s.up,s.right,s.down,s.left)
	k.register_keypress('q', wd.stop)
	k.start()
	
	wd.set_scene(s)
	wd.start()
	return wd,s

		
if __name__ == '__main__':
	wall_test()	

		
		
