from scenes import PlayableScene
import random
from walldriver import PANEL_NUM, WallDriver

W = 8
H = 4

class Snake(PlayableScene):
	
	
	def __init__(self,bg=(0,0,0),snake=(0,240,0),apple=(255,0,0),snake_max_len=4):
		self.bg_color = bg
		self.snake_color = snake
		self.apple_color = apple
	
		self.snake_at = []
		self.snake_max_len = snake_max_len
		
		self.apples_at = []
		
		self.snake_reset()
		self.apple_reset()
		
		super(Snake,self).__init__(tempo=120)
		
	def apple_reset(self):
		self.apples_at = [(random.randint(0,H),random.randint(0,W))]
		
	def snake_reset(self):
		self.snake = []
		self.snake_at.append((random.randint(0,H),random.randint(0,W)))
		
	
	def _snake_step(self):
		
		if self.snake_at[-1] in self.apples_at:
			self.snake_reset()
			self.apple_reset()
		
		old_len = len(self.snake_at)
		while old_len == len(self.snake_at:
			r = random.randint(0,4)
			if r == 0:
				self.snake_at.append((self.snake_at[-1][0],self.snake_at[-1][1]+1))
			elif r == 1:
				self.snake_at.append((self.snake_at[-1][0]+1,self.snake_at[-1][1]))
				
			elif r == 2:
				self.snake_at.append((self.snake_at[-1][0],self.snake_at[-1][1]-1))
				
			else: # r == 3
				self.snake_at.append((self.snake_at[-1][0]-1,self.snake_at[-1][1]))
			
			if self.snake_at[-1] in self.snake_at[:-1]:
				self.snake_at.pop()
	
		if len(self.snake_at) >= self.snake_max_len:
			self.snake_at.pop(0)
			
		# Handle out of bounds
		if self.snake_at[-1][0] < 0:
			self.snake_at[-1] = (self.snake_at[-1][0]+2,self.snake_at[-1][1])
		elif self.snake_at[-1][1] < 0:
			self.snake_at[-1] = (self.snake_at[-1][0],self.snake_at[-1][1]+2)
		elif self.snake_at[-1][0] >= H:
			self.snake_at[-1] = (self.snake_at[-1][0]-2,self.snake_at[-1][1])
		elif self.snake_at[-1][1] >= W:
			self.snake_at[-1] = (self.snake_at[-1][0],self.snake_at[-1][1]-2)
		
	
	def _convert_to_2d(self,i):
		return (i%H,i/H)
	
	
	def step(self,seconds):
		if not super(Snake,self).step(seconds):
			return False
			
		for i in xrange(self.beats()):
			self._snake_step()
			print "Snake at %s,%s" % self.snake_at[-1]
		
		return True
	
	
	def rgb(self):
		
		rgb_now = []
		
		for i in xrange(PANEL_NUM):
			
			if self._convert_to_2d(i) in self.snake_at:
				rgb_now.append(self.snake_color)
			elif self._convert_to_2d(i) in self.apples_at:
				rgb_now.append(self.apple_color)
			else:
				rgb_now.append(self.bg_color)
			
			
			
		# Hack to fix switched panels
		x = rgb_now[18]
		rgb_now[18] = rgb_now[19]
		rgb_now[19] = x
	
		return rgb_now	
		
def wall_test():
	
	wd = WallDriver(refresh=30,host='localhost',port=7778)
	wd.set_scene(Snake())
	wd.start()
	return wd

		
	
		
		
		
