import threading
import Queue


class DummyTrack(object):

	def step(self,beats):
		print "Dummy: I was told to step ahead %s beats." % beats
	
	def scene_data(self):
		return SceneData(None,None,None)

class Track(object):
	
	bad_mod_text = "You can't alter track data while it is being read."
	
	def __init__(self):
		self.scene_data = []
		self.started_iter = False
		self._step = None
	
	def __len__(self):	
		last_beat,si = self.scene_data[-1]
		return last_beat+1
	
	def T(object):
		def __init__(self,scene_datum,beat):
			self.scene_datum = scene_datum
			self.beat = beat
			
		def __cmp__(self,other):
			return cmp(self.beat,other.beat)
	
	def set_scene_datum(self,scene_datum,beat):
		if started_iter:
			raise ValueError,bad_mod_text
		
		si = T(scene_datum,beat)
		i = bisect.bisect_left(self.scene_data,si)
		if self.scene_data[i].beat == beat:
			self.scene_data[i] = si
		else:
			self.scene_data.insert(i,si)
		
	
	
	def delete_scene_datum(self,beat):
		if started_iter:
			raise ValueError,bad_mod_text
			
		i = bisect.bisect_left(self.scene_data,si)
		if self.scene_data[i].beat == beat:
			return self.scene_data.pop(i)
	
	
	
	def at_beat(self,beat):
		i = bisect.bisect_left(self.scene_data,si)
		if self.scene_data[i].beat == beat:
			return self.scene_data[i]
	
	##############################
	### Default track walker
	
	def step(self):
		if not self._step:
			self._step = self.timing()
		yield self._step.next()
	
	def reset_step(self,cursor):
		self._step = None
	
	
	
	
	##################################
	### Iterate through the Track
	
	def __iter__(self):
		self.started_iter = True
		for tsi in self.scene_data:
			yield tsi.beat, tsi.scene_datum
		self.started_iter = False
	
	def iterbeats(self):
		self.started_iter = True
		t_iter = iter(self)
		beat,si = t_iter.next()
		for i in xrange(len(self)):
			if beat == i:
				yield beat,si
				beat,si = t_iter.next()
			else:
				yield beat,None
		self.started_iter = False
			
	def instances(self):
		self.started_iter = True
		for tsi in self.scene_data:
			yield tsi.scene_datum
		self.started_iter = False




class TrackPlayer(threading.Thread):
	
	SLEEP_TIME = 0.2
	
	def __init__(self,wall_driver):
		
		# DEBUG
		self.scene_db = DummyDB()
		
		#self.scene_db = SceneDB()
		self.wall_driver = wall_driver
		
		# Track handlers
		self._track_queue = Queue.Queue()
		self._stop = threading.Event()
		
		self._iteration = 0
		
		super(TrackPlayer,self).__init__()

	def stop(self):
		""" Stops driving the wall
		"""
		self._stop.set()
		self._track_queue.put('dummy')

	def stopped(self):
		""" True if the thread should stop execution
		"""
		return self._stop.isSet()
	
		
	def enqueue_track(self,track):
		self._track_queue.put(track)
		
		
	def run(self):
		
		cur_track = None
		last_beats = None
		
		while not self.stopped():
			
			if not cur_track:
				cur_track = self._track_queue.get()
				if self.stopped(): break
				
			cur_beats = self.wall_driver.beats
			cur_scene_data = None
			if cur_track.step(0 if not last_beats else cur_beats - last_beats):
				cur_scene_data = cur_track.scene_data()
			
			# If there is new scene data, then tell that to the wall driver
			if cur_scene_data:
				self.wall_driver.set_scene( \
					self.scene_db.get(new_scene_data).bind(new_scene_data) \
				)
			last_beats = cur_beats
			
			time.sleep(TrackPlayer.SLEEP_TIME) # We only need to check
			self._iteration += 1
		
	
