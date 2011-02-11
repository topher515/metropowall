from scenes import PlayableScene
import random
from walldriver import PANEL_NUM, WallDriver, KeyboardHandler, WALL_HEIGHT, WALL_TOP_WIDTH


W = WALL_TOP_WIDTH
H = WALL_HEIGHT

from collections import defaultdict




class Snake(PlayableScene):
	
	
	def __init__(self,bg=(0,0,0),snake=(0,240,0),apple=(255,0,0),snake_max_len=4):
		self.bg_color = bg
		self.snake_color = snake
		self.apple_color = apple
		self.points_color = (255,255,255)
	
		self.snake_at = []
		self.snake_max_len = snake_max_len
		
		self.apples_at = []
		self.apple_time = 0
		
		self.snake_reset()
		self.apple_reset()
		
		self.points = 0
		
		self._snake_dir = random.randint(0,4) 
		
		super(Snake,self).__init__(tempo=360)
		
	def apple_reset(self):	
		self.apple_time = 0
		self.apples_at = [(random.randint(0,W),random.randint(0,H))]
		
	def snake_reset(self):
		self.snake = []
		self.snake_at.append((random.randint(0,W),random.randint(0,H)))
		
	
	def up(self): self._snake_dir = 0
	def right(self): self._snake_dir = 1
	def down(self): self._snake_dir = 2
	def left(self): self._snake_dir = 3
	
	def _snake_step(self):
		
		if self.snake_at[-1] in self.apples_at:
		#	self.snake_reset()
			self.apple_reset()
			self.points += 1
		
		#old_len = len(self.snake_at)
		#while old_len == len(self.snake_at):
		r = self._snake_dir
		if r == 0:
			self.snake_at.append((self.snake_at[-1][0],self.snake_at[-1][1]-1))
		elif r == 1:
			self.snake_at.append((self.snake_at[-1][0]+1,self.snake_at[-1][1]))
			
		elif r == 2:
			self.snake_at.append((self.snake_at[-1][0],self.snake_at[-1][1]+1))
			
		else: # r == 3
			self.snake_at.append((self.snake_at[-1][0]-1,self.snake_at[-1][1]))
		
		#if self.snake_at[-1] in self.snake_at[:-1]:
		#	self.snake_at.pop()
	
		if len(self.snake_at) >= self.snake_max_len:
			self.snake_at.pop(0)
			
		# Handle out of bounds
		if self.snake_at[-1][0] < 0:
			self.snake_at[-1] = (W,self.snake_at[-1][1])
		elif self.snake_at[-1][1] < 0:
			self.snake_at[-1] = (self.snake_at[-1][0],H)
		elif self.snake_at[-1][0] >= W:
			self.snake_at[-1] = (0,self.snake_at[-1][1])
		elif self.snake_at[-1][1] >= H:
			self.snake_at[-1] = (self.snake_at[-1][0],0)
		
	
	def _convert_to_2d(self,i):
		return (i/H,i%H)
	
	
	def step(self,seconds):
		if not super(Snake,self).step(seconds):
			return False
		#print 'step %s' % seconds	
			
		for i in xrange(int(self.beats())):
			self._snake_step()
			self.apple_time += 1
			if self.apple_time >= 10:
				self.apple_reset()
		
		return True
	
	
	def rgb(self,):
		
		rgb_now = []
		
		points_counted = 0
		
		for i in xrange(PANEL_NUM):
			
			_2d = self._convert_to_2d(i)
			if _2d in self.snake_at:
				#print 'Paint snake at %s,%s (panel %s)' % (_2d[0],_2d[1],i)
				rgb_now.append(self.snake_color)
				points_counted += 1
			elif _2d in self.apples_at:
				rgb_now.append(self.apple_color)
				points_counted += 1
			else:
				if self.points >= PANEL_NUM:
					rgb_now.append((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
				else:
					
					if points_counted < self.points:
						rgb_now.append(self.points_color)
						points_counted += 1
					else:
						rgb_now.append(self.bg_color)
			
			
			
		# Hack to fix switched panels
		x = rgb_now[14]
		rgb_now[14] = rgb_now[15]
		rgb_now[15] = x
	
		return super(Snake,self).rgb(rgb_now)	
		
def wall_test():
	
	print """
	SNAKE for METROPOWALL
	
	Arrow keys control. Press 'q' to exit.
	
	Collect all the apples to win a special surprise!
	
	"""
	
	wd = WallDriver(refresh=10,host='localhost',port=7778)
	
	k = KeyboardHandler()
	
	s = Snake()
	
	k.register_arrows(s.up,s.right,s.down,s.left)
	k.register_keypress('q', wd.stop)
	k.start()
	
	wd.set_scene(s)
	wd.start()
	return wd,s

		
if __name__ == '__main__':
	wall_test()	

		
		
