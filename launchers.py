from walldriver import WallDriver, KeyboardHandler
from sprites import Sprite, SpritePlane
from random import randint as rint
rand_rgb = lambda: (rint(0,255),rint(0,255),rint(0,255))

class LauncherScene(SpritePlane):
	

	def __init__(self):
		
		self.launchers = []
		SpritePlane.__init__(self,tempo=360)
		
	def add_random_launcher(self):
		self.launchers.append(
			SpriteLauncher(color=rand_rgb(),delay=rint(3,7),scene=self)
		)
		self.add_sprite(*self.random_visible_plane2d(),sprite=self.launchers[-1])


	def step(self,seconds):
		
		if not SpritePlane.step(self,seconds):
			return False
		
		if self.beats_in_step > 0:	
			for l in self.launchers:
				l.tick()
			
		return True


class SpriteLauncher(Sprite):
	
	def __init__(self,**kwargs):
		self.delay = kwargs.pop('delay')
		self.scene = kwargs.pop('scene')
		self.count = self.delay
		Sprite.__init__(self,**kwargs)
	
	def tick(self):
		self.count -= 1
		if self.count < 0:
			loc = self.scene.loc_by_sprite[self]
			self.scene.add_sprite(*loc,\
				sprite=Sprite(color=self.rgb(),vector=(rint(-1,1),rint(-1,1)))
			)
			self.count = self.delay


def launcher_test():
	k = KeyboardHandler()
	l = LauncherScene()
	k.register_keypress('p',l.add_random_launcher)
	k.start() # Start watching keyboard
	
	wd = WallDriver(refresh=15,port=7778,initial_scene=l)
	k.register_keypress('q', wd.stop)
	wd.start()
	
	
if __name__ == '__main__':
	launcher_test()
		