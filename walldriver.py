import pickle
import socket
import threading
import bisect
import time
import random
import errno

DEFAULT_TCP_IP = '127.0.0.1'
DEFAULT_TCP_PORT = 5005
BUFFER_SIZE = 1024

SCENE_DATA_PATH = 'scene.dat'

PANEL_NUM = 36

DEBUG = True


##### DEBUGGING


class DummyDB(object):
	def get(self,k):
		return DummyScene()
	def bind(self,scene_data):
		return DummyScene.bind(scene_data)

#### END DEBUGGING



class SceneData(object):	
	def __init__(self,scene_id,colors,tempo):
		self.colors = colors
		self.scene_id = scene_id
		self.tempo = tempo
		
	def add_color(self,rgb):
		color_num = len(self.colors)
		self.colors.append(rgb)
		return color_num
	

	

class SceneDB(object):

	def __init__(self):
		self.db = []
		self.load()

	def load(self,filename=SCENE_DATA_PATH):
		# Load scene data from file
		if os.path.isfile(filename):
			f = open(filename,'r')
			data = pickle.load(f)
			f.close()
			if SceneTemplate.version != data['version']:
				raise ValueError,'Incompatible Versions!'
			self.db = data['scenes']
			print "Loaded %s v%s scenes from %s" % \
				(len(self.db),Scene.version,f.name)
		else:
			print "Didn't find any scene data. Looked here: %s" % filename

	def bind(self,scene_data):
		"""Convenience method for getting a scene from scene data and
		binding that data to the scene
		"""
		return self.get(scene_data.scene_id).bind(scene_data)

	def get(self,id):
		try:
			return self.db[id]
		except ValueError:
			raise ValueError,'Scene Number %s does not exist in the DB' % id

	def add(self,scenes):
		if type(scenes) == Scene:
			scenes = [scenes]
		self.db += scenes
		self.save()
		
	def remove(self,number):
		try:
			return self.db.pop(number)
		except ValueError:
			raise ValueError,"Unable to delete scene number %s--it doesn't exist in the DB." % number
		

	def save(self,filename=SCENE_DATA_PATH):
		f = open(filename,'w')
		pickle.dump({'version':Scene.version,'scenes':self.db},f)
		f.close()
		



class WallDriver(threading.Thread):
	
	panel_num = PANEL_NUM
	
	
	def __init__(self,host=DEFAULT_TCP_IP,port=DEFAULT_TCP_PORT,refresh=60,initial_scene=None):
		# Scene data
		# self.scene_db = SceneDB()
		self.refresh = refresh
		
		self.host = host
		self.port = port
		
		# Enables stopping the driver
		self._stop = threading.Event() # This is how we'll mark the thread for stopping
				
		# Beat counter
		self.beats = 0
		
		self.start_time = None
		self._iteration = 0
		
		# The scene that is currently playing
		self._cur_playing_scene = None
		self._scene_lock = threading.Lock() # We'll need to do some locking
		
		if initial_scene:
			self.set_scene(initial_scene)
		
		super(WallDriver,self).__init__()
		
	
	def _set_refresh(self,val):
		self._refresh = val
		self._sleep_time = 1/float(val)
	def _get_refresh(self):
		return self._refresh
	refresh = property(fset=_set_refresh,fget=_get_refresh,doc='Refresh rate in hertz')
	
	def _reconnect(self):	
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(.2)
		self.sock.connect((self.host, self.port))
		self.sock.setblocking(0)
		
	def _disconnect(self):
		self.sock.close()
		
	def stop(self):
		""" Stops driving the wall
		"""
		self._stop.set()

	def stopped(self):
		""" True if the thread should stop execution
		"""
		return self._stop.isSet()	
	
	
	def set_scene(self,playable_scene):
		self._scene_lock.acquire()
		print 'New scene set: %s' % playable_scene
		self._cur_playing_scene = playable_scene
		self._scene_lock.release()
	
	def run(self):
		
		self.start_time = time.time()
		last_time = None
		
		while not self.stopped():
			
			# Determine data to send to the wall (max)
			cur_time = time.time()
			wall_data = None
			self._scene_lock.acquire()
			if self._cur_playing_scene.step(0 if not last_time else cur_time - last_time):
				wall_data = self._cur_playing_scene.rgb()
				# print wall_data
				self.beats += self._cur_playing_scene.beats()
			else:
				print 'skip...',
				pass # No change so we won't send scene data
			self._scene_lock.release()
			last_time = cur_time
			
			# Send the data to the wall (max)
			if wall_data:
				self.send(wall_data)
			
			time.sleep(self._sleep_time) # So we don't overwhelm max
			self._iteration += 1
		
		
	def send(self,data):
		try:
			self._reconnect()
		

			l = []
			for i,rgb in enumerate(data):
				for j,color in enumerate(rgb,1):
					l.append('%s %s' % (i*3+j,color))
					
			#print 'sending...',
			self.sock.send('\n'.join(l))
			#print ' sent.'

			self._disconnect()
		except socket.error, e:
			if isinstance(e.args, tuple):
				#print "errno is %d" % e[0]
				if e[0] == errno.EPIPE:
					print "Remote disconnect!"
				else:
					raise
		
	
	def pause(self):
		raise ValueError, "Not Yet Implemented!"
		




		
"""class MidiTrack(object):

	def __init__(self, speed=80, panels=[], width=10,height=4):
		self.speed = speed
		self.width= width
		self.height = height

		if panels:
			self.panels = panels
		else:
			self.panels = []
			self.panels.append(Panel())

		self.tracks = [[]]

	def add_panel_event(self,panel_x,panel_y,time,color):
		pass

	def add_event(self,panels,event):
		bisect.insort(self.tracks[-1],event)

	def _get_midi(self):

		midi_header = ['\x4D\x54\x68\x64\x00\x00\x00\x06', # This is a midi file
			'\x00\x01', # Type 1
			struct.pack('>h',len(self.tracks)), # number of tracks
			struct.pack('>h',self.speed), # Speed
			]
		track_header = '\x4D\x54\x72\x6B'
		trackout = '\x00\xFF\x2F\x00'

		tracks_hex = []

		for track in self.tracks:
			bytes_in_track = sum([len(event) for event in track])
			len_hex = struct.pack('>i',bytes_in_track+len(trackout))

			last_event = None
			for events in self.track:
				if not last_event:

				else:


				track_hex = 

			tracks_hex.append(track_header+len_hex+track_hex)+trackout)

		midi_data = ''.join(midi_header + track_hex)
		return midi_data


	midi = property(fget=_get_midi)

	def writefile(self,filename,overwrite=True):
		if os.path.isfile(filename) and not overwrite:
			raise Exception,'File already exists.'
		open(filename,'wb').write(self.midi)
"""
