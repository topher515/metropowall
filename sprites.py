from scenes import PlayableScene
from collections import defaultdict
from walldriver import WALL_HEIGHT, WALL_TOP_WIDTH, WALL_BOTTOM_WIDTH, PANEL_NUM
import random

class SpritePlane(PlayableScene):
	
	def __init__(self,*args,**kwargs):
	
		self.bg = kwargs.pop('bg',(0,0,0))
			
		self.wrap = kwargs.pop('wrap',True)
			
		self.sprites_by_loc = defaultdict(list)
		self.loc_by_sprite = {}
		self.tile_0_in_plane2d = (0,0)
		
		super(SpritePlane,self).__init__(*args,**kwargs)
		
		self.trails_by_wall1d = {}
		
	def add_sprite(self,x,y,sprite):
		
		# Perform wrapping if this plane is set to wrap
		if self.wrap:
			wx,wy = self.plane2d_to_wall2d(x,y)
			
			if not 0 <= wy < WALL_HEIGHT: 
				wy = wy % WALL_HEIGHT
			
			assert(0 <= wy < WALL_HEIGHT)
			if wy <= 1:
				if not 0 <= wx < WALL_TOP_WIDTH:
					wx = wx % WALL_TOP_WIDTH
			else:
				if not -1 <= wx < WALL_BOTTOM_WIDTH-1:
					wx = (wx % WALL_BOTTOM_WIDTH) - 1
				
			x,y = wx,wy		
		
		sprite._plane = self
		self.sprites_by_loc[(x,y)].append(sprite)
		self.loc_by_sprite[sprite] = (x,y)
		
	def remove_sprite_xy(self,x,y):
		for s in self.at(x,y):
			self.remove_sprite(s)
	
	def remove_sprite(self,sprite):
		loc = self.loc_by_sprite[sprite] # Get sprite loc
		self.trails_by_wall1d[loc] # Add trail
		del self.loc_by_sprite[sprite] # Remove loc from dict
		self.sprites_by_loc[loc].remove(sprite) # Remove this sprite from loc list
	
	
	
	def at(self,x,y):
		return self.sprites_by_loc((x,y))
	
	def move_to(self,sprite,x,y):
		cx,cy = self.loc_by_sprite[sprite]
		self.remove_sprite(sprite)
		self.add_sprite(sprite,x,y)
		
	def move(self,sprite,x,y):
		cx,cy = self.loc_by_sprite[sprite]
		self.move_to(sprite,cx+x,cx+y)
		
	def move_up(self,sprite): self.move(sprite,0,1)	
	def move_right(self,sprite): self.move(sprite,1,0)
	def move_down(self,sprite): self.move(sprite,0,-1)	
	def move_left(self,sprite): self.move(sprite,-1,0)
	
	def random_visible_plane2d(self):
		return self.wall1d_to_plane2d(random.randint(0,PANEL_NUM))
	
	def plane2d_is_visible(self,x,y):
		return PANEL_NUM > self.plane2d_to_wall1d(x,y) >= 0
	
	def wall1d_to_wall2d(self,i):	
		if i == 32:
			return (-1,2)
		elif i == 33:
			return (-1,3)
		
		return (i/WALL_HEIGHT,i%WALL_HEIGHT)
	
	def wall1d_to_plane2d(self,i):
		return self.wall2d_to_plane2d(wall1d_to_wall2d(i))
		
		
	def wall2d_to_plane2d(self,x,y):
		return x+self.tile_0_in_plane2d[0],y+self.tile_0_in_plane2d
	
	def plane2d_to_wall2d(self,x,y):
		return x-self.tile_0_in_plane2d[0],y-self.tile_0_in_plane2d
	
	def wall2d_to_wall1d(self,x,y):
		if x,y == (-1,2):
			return 32
		elif x,y == (-1,3):
			return 33
		
		return x*WALL_HEIGHT+y
	
	def plane2d_to_wall1d(self,x,y):
		return self.wall2d_to_wall1d(self.plane2d_to_wall2d(x,y))
	
	
	def step(self,seconds):
		
		super(SpritePlane,self).step(seconds)
	
		if 
	
	
	def rgb(self,base_rgb=None):
		rgb_now = []
		
		for i in xrange(PANEL_NUM):
			
			_2d = self.wall1d_to_plane2d(i)
			sprites = self.sprites_by_loc(_2d)
			
			to_blend = []
			top_sprite = None
			# Loop through sprites at this location
			# collect all the ones which are blendable
			for s in sprites:
				if not top_sprite or top_sprite.z < s.z:
					top_sprite = s
				if s.blend:
					to_blend.append(x)
			# If the top sprite is a blendable one,
			# then use the blended color
			if top_sprite.blend:
				rgb_now.append(self.blend_rgbs([x.rgb() for x in to_blend]))
			# If the top sprite is not blendable then just
			# use its color
			else:
				rgb_now.append(top_sprite.rgb())
				
		# If we got a
		if base_rgb:
			rgb_now = self.blend_rgb_list(base_rgb,rgb_now)
		
		return super(SpritePlane,self).rgb(rgb_now)
	
	
class Sprite(object):
	
	def __init__(self,color,blend = True, z=0, trail=0):
		if type(color) == type(self.__init__):
			self.color_fn = color
			self.color = None
		else:
			self.color = color
			self.color_fn = None
			
		self.blend = blend
		self.z = z
		self.trail = trail
	
	def loc(self):
		if not self._plane:
			raise ValueError,'Sprite %s is not on a plane, so it has no location!' % self
		return self._plane.loc_by_sprite[self]
		
	def rgb(self):
		return self.color or self.color_fn()