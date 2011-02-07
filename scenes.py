import bisect
from math import floor as flr
from sortedcollection import SortedCollection
from operator import itemgetter

from walldriver import PANEL_NUM


### For Debugging

class DummyScene(object):
	def bind(self,scene_data):
		return Reset()
	
	

#########################
### Simple Playable Scenes
#########################	

class PlayableScene(object):
	
	def __init__(self,tempo=120):
		self.tempo = tempo
		
		self.total_seconds = 0
		self.seconds_in_step = 0
		#self.seconds_in_scene = 0
		self.total_beats = 0
		self.beats_in_step = 0
		#self.beats_in_scene = 0
		
	
	def bpm(self): return self.tempo # Beats per minute
	def bps(self): return float(self.tempo)/60.0 # Beats per second
	def spb(self): return 1/self.bps() # Seconds per beat
	
	def step(self,seconds):
		"""Returns true if calling step with 
		the given value had any perceptible effect. 
		"""
		if seconds == 0:
			return False
		
		# Save the old values
		last_secs = self.total_seconds
		last_beat = flr(self.bps()*self.total_seconds)
		# Set the new values
		self.seconds_in_step = seconds
		self.total_seconds += seconds
		this_beat = flr(self.bps()*self.total_seconds)
		# If we went through a beat
		if last_beat < this_beat:
			self.beats_in_step = this_beat - last_beat
			self.total_beats = this_beat
		else:
			self.beats_in_step = 0 # No beats occurred this time
		
		return True
		
	
	def beats(self):
		return self.beats_in_step
		
	def rgb(self): pass
	

class RandomFlashing(PlayableScene):		
	def rgb(self):
		return [(random.randint(0,255),random.randint(0,255),random.randint(0,255)) \
		 	for i in xrange(PANEL_NUM)]


class Reset(PlayableScene):
	def rgb(self): return [(0,0,0)]*PANEL_NUM



#########################
### Scene Templates
#########################

class SceneTemplate(object):
	version = 0.2
	
	
	def __init__(self,scene_length):
		""" `scene_length` is the number of beats in this scene
		"""
		self.scene_length = scene_length
	
	
	def bind(self,scene_data):
		""" Accept a `scene_data` dictionary and return a
		`PlayableScene` object
		"""
		raise ValueError,'This method must be overriden by a subclass'
		
		
	def __len__(self):
		return self.scene_length
	
	
class KeyframeSceneTemplate(SceneTemplate):


	class KeyframePlayableScene(PlayableScene):
		
		def __init__(self,scene_template,**kwargs):
				
			self.colors = kwargs.pop('colors')
			PlayableScene.__init__(self,**kwargs)
			self.scene_template = scene_template
			
			self.seconds_in_scene = 0
			self.beats_in_scene = 0
			
			self._prev_frame = None # The previous frame before 'now'
			self._next_frame = None # The next frame after 'now'
			self._prev_at = None # The time in seconds at which the previous frame occurred
			self._next_at = None # The time in seconds at which the next frame will occur
			self._prev_rgb = None # [(0,0,0)]*PANEL_NUM
			self._next_rgb = None #[(0,0,0)]*PANEL_NUM
			
		def step(self,seconds):
			if not PlayableScene.step(self,seconds):
				# If the nothing happened in this step, then don't bother with calc
				# this probably just means that seconds = 0
				return False
				
			self.seconds_in_scene += seconds
			self.beats_in_scene += self.beats_in_step
			if self.beats_in_scene > self.scene_template.scene_length:
				self.beats_in_scene = self.beats_in_scene % self.scene_template.scene_length
				self.seconds_in_scene = self.seconds_in_scene % (self.scene_template.scene_length*self.spb())
			
			return True # Remember to return True or nothing happens!
			
			
		def rgb(self):
			if not self._prev_frame or not self._next_frame or self.beats() != 0:
				old_prev_frame = self._prev_frame
				old_next_frame = self._next_frame
				try:
					self._prev_frame = self.scene_template._keyframes.find_le(self.beats_in_scene)
				except ValueError:
					# If we can't find a key less than this beat then this is the beginning
					# so use the last frame
					self._prev_frame = self.scene_template._keyframes[-1]
				try:
					self._next_frame = self.scene_template._keyframes.find_gt(self.beats_in_scene)
				except ValueError:
					# If we can't find a key great than this beat then this is the end so
					# use the first frame
					self._next_frame = self.scene_template._keyframes[0]
					
				# If the keyframes have changed, recalculate rgb values
				if old_prev_frame != self._prev_frame and old_next_frame == self._next_frame: 
					
					self._prev_at = self._prev_frame[0]*self.spb()
					self._next_at = self._next_frame[0]*self.spb()
					assert(self._prev_at < self.seconds_in_scene)
					assert(self._next_at > self.seconds_in_scene)
				
					self._prev_rgb = [self.colors[x] for x in self._prev_frame[1].panel_colors]
					self._next_rgb = [self.colors[x] for x in self._next_frame[1].panel_colors]
					
			# If the next keyframe is a 'switch to' frame
			if isinstance(self._next_frame[1],KeyframeSceneTemplate.SwitchToFrame):
				# then just play the previously calculated rgb
				return self._prev_rgb # Just play the previous
			elif isinstance(self._next_frame[1],KeyframeSceneTemplate.FadeToFrame):
				# Calculate the rgb for 'now'
				
				#      seconds after the last keyframe  OVER  total seconds between keyframe
				progress = (self.seconds_in_scene - self._prev_at) / (self._next_at - self._prev_at)
				assert(0 < progress < 1)
				
				now_rgb = []
				
				# Look at each panel
				for i in xrange(PANEL_NUM):
					now_rgb.append( \
						((self._next_rgb[i] - self._prev_rgb[i])*progress) + self._prev_rgb \
					)
					
				return now_rgb 
			
			else:
				raise ValueError, 'Unknown frame type encountered %s at %s' % (self._next_frame[1],self._next_frame[0])
	
	
	def __init__(self,scene_length):
		self._keyframes = SortedCollection(key=itemgetter(0))
		self.scene_length = scene_length
		
	
	def set_wall_frame(self,at_beat,panel_color,fade_to=True):
		return self.set_frame(at_beat,[panel_color]*PANEL_NUM,fade_to)
	
	def set_frame(self,at_beat,panel_colors,fade_to=True):
		"""`panel_colors` is either a list which is the same length
		as the number of panels in the lightwall and whose content
		is an integer 'color id' OR it is a dictionary with
		keys that are integer values no greater than the number 
		of panels in the lightwall and whose value is a integer 'color id'.
		e.g., [3,1,None,4,...] is equivalent to {1:3,2:1,4:4}
		
		# If there is already a keyframe at the given beat, it is overwritten
		"""
		if type(at_beat) != int:
			print "Warning: settings non-integer beat"
		
		if type(panel_colors) == dict:
			l = []
			for i in xrange(PANEL_NUM):
				l.append(panel_colors.get(i,None))
			panel_colors = l
		
		if at_beat < 0:
			raise ValueError,"Tried to add a keyframe before beginning of scene (<0)"
		elif at_beat > self.scene_length:
			raise ValueError, "Tried to add a keyframe after end of scene (>scene_length)"
		
		
		try:
			# try to remove a keyframe at that beat because we want to
			# overwrite it if there's one there
			self._keyframes.remove(self._keyframes.find(at_beat))
		except ValueError:
			pass
		
		if fade_to:
			self._keyframes.insert((at_beat,KeyframeSceneTemplate.FadeToFrame(panel_colors)))
		else:
			self._keyframes.insert((at_beat,KeyframeSceneTemplate.SwitchToFrame(panel_colors)))
		
		
	def remove_frame(self,at_beat):
		self._keyframes.remove(self._keyframes.find(at_beat))

				
	
	def bind(self,scene_data):
		return KeyframeSceneTemplate.KeyframePlayableScene(self,**scene_data)
		
	
	
	class Frame(object):
		def __init__(self,panel_colors):
			self.panel_colors = panel_colors
	class FadeToFrame(Frame): pass
	class SwitchToFrame(Frame): pass
	
	
	
			

		
	

