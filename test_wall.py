from walldriver import WallDriver
from trackplayer import TrackPlayer, DummyTrack

from scenes import KeyframeSceneTemplate

def test_trackplayer():
	
	wall_driver = WallDriver()
	print "Started wall driver for %s panel wall at %s:%s" % \
		(wall_driver.panel_num, wall_driver.host, wall_driver.port)
	track_player = TrackPlayer(wall_driver)
	track_player.enqueue_track(DummyTrack())
	return wall_driver,track_player
	
	
	
def test_keyframescene():
	
	wall_driver = WallDriver(refresh=30,port=7778)
	print "Started wall driver for %s panel wall at %s:%s" % \
		(wall_driver.panel_num, wall_driver.host, wall_driver.port)
	
	kst = KeyframeSceneTemplate(scene_length=32) # Length of scene in beats
	
	# Set all panels to color 0 at beat 0
	kst.set_wall_frame(0,0)
	
	# Set all panels to color 1 at beat 10, except for panel 6 set to color 2
	x = [1]*36
	x[6] = 2
	kst.set_frame(10,x)
	
	# set all panels to color 2 at beat 20
	kst.set_wall_frame(20,2)
	
	p = kst.bind({'tempo':116,
		'colors':{
			0:(12,34,56),
			1:(255,234,204),
			2:(118,0,6),
		}
	})
	
	# p is now a playable scene
	wall_driver.set_scene(p)
	wall_driver.start()
	return wall_driver,kst
	
if __name__ == '__main__':
	test_keyframescene()
	