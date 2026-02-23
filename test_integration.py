import time
from Core_Engine import CoreEngine

def test_integration():
    engine = CoreEngine()
    
    print("Submitting song...")
    session_id = engine.submit_song("https://soundcloud.com/mock/track", 10.0)
    print(f"Session created: {session_id}")
    
    print("Confirming payment...")
    success = engine.confirm_payment(session_id)
    assert success is True
    
    print("Checking queue...")
    queue = engine.get_queue()
    assert len(queue) == 1
    assert queue[0]['soundcloud_id'] == "mock_track_123"
    print("Song successfully added to queue via CoreEngine.")
    
    print("Popping song...")
    next_song = engine.pop_next()
    assert next_song['soundcloud_id'] == "mock_track_123"
    print("Integration test passed!")

if __name__ == "__main__":
    test_integration()
