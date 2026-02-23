import time
import sys
import os

# Ensure we can import engine efficiently
sys.path.append(os.getcwd())

from engine import MusicQueue

def test_music_queue():
    queue = MusicQueue()
    
    # Increase time weight to make test faster/obvious
    queue.time_weight = 0.5 # 0.5 bid equivalent per second

    print("Adding Song A (Bid 10.0)")
    queue.add_song("song_A", 10.0)
    
    time.sleep(2)
    
    print("Adding Song B (Bid 10.5)")
    queue.add_song("song_B", 10.5)
    
    # At this point:
    # Song A: Bid 10.0, Waited 2s -> Score ~ 11.0
    # Song B: Bid 10.5, Waited 0s -> Score ~ 10.5
    # Expect Song A to come out first despite lower bid because of wait time
    
    print("\nQueue Status:")
    for item in queue.get_queue_status():
        print(item)
        
    next_song = queue.get_next_song()
    print(f"\nNext song popped: {next_song['soundcloud_id']} (Score: {next_song['final_score']:.2f})")
    
    assert next_song['soundcloud_id'] == "song_A", "Error: Song A should be first due to wait time boost"
    
    next_song_2 = queue.get_next_song()
    print(f"Next song popped: {next_song_2['soundcloud_id']} (Score: {next_song_2['final_score']:.2f})")
    
    assert next_song_2['soundcloud_id'] == "song_B", "Error: Song B should be second"
    
    print("\nTest Passed!")

if __name__ == "__main__":
    test_music_queue()
