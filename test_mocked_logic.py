from unittest.mock import MagicMock
import os
from Core_Engine import CoreEngine
import soundcloud_client
import stripe_client

def test_core_logic_mocked():
    # 1. Mock the external clients to avoid network dependency
    soundcloud_client.soundcloud_client.resolve_track = MagicMock(return_value={
        "id": "mock_id_999",
        "title": "Mocked Song",
        "user": {"username": "Mock Artist"},
        "duration": 200000
    })
    
    stripe_client.stripe_client.create_checkout_session = MagicMock(return_value="mock_session_xyz")
    
    # 2. Initialize Engine
    print("Initializing CoreEngine...")
    engine = CoreEngine()
    
    # 3. Submit song
    print("Testing Submission (Mocked Network)...")
    session_id = engine.submit_song("https://soundcloud.com/test", 25.0)
    assert session_id == "mock_session_xyz"
    print(f"Submission OK. Session: {session_id}")
    
    # 4. Confirm Payment
    print("Testing Payment Confirmation...")
    success = engine.confirm_payment(session_id)
    assert success is True
    print("Payment Confirmation OK.")
    
    # 5. Verify Queue
    print("Verifying MusicQueue Integration...")
    queue = engine.get_queue()
    assert len(queue) == 1
    assert queue[0]['soundcloud_id'] == "mock_id_999"
    assert queue[0]['bid'] == 25.0
    print("Queue Integration OK.")
    
    print("\nCORE LOGIC VERIFIED: Everything is connected correctly!")

if __name__ == "__main__":
    test_core_logic_mocked()
