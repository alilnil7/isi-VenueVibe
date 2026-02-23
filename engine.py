import time
import heapq
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass(order=True)
class QueueItem:
    score: float
    timestamp: float
    bid: float
    soundcloud_id: str = field(compare=False)

    def __post_init__(self):
        # heapq is a min-heap, so we negate the score to simulating a max-heap behavior for the score
        # efficiently. However, we want strict ordering. 
        # Actually, let's keep it simple: store as tuple (-score, timestamp, ...) so 
        # highest score comes first (min neg-score).
        pass

class MusicQueue:
    def __init__(self):
        self.queue = [] # List of QueueItem
        # Configurable weight for time. 
        # Example: 1 minute waiting adds equivalent of 0.1$ to the bid?
        # Let's say 1 cent per minute = 0.01 / 60 per second.
        # This is adjustable.
        self.time_weight = 0.01 / 60 

    def add_song(self, soundcloud_id: str, bid: float):
        """
        Adds a song to the queue.
        """
        timestamp = time.time()
        # Initial score is just the bid. 
        # Since the score changes over time (wait time increases), 
        # simple heap won't work for dynamic re-scoring without re-heapifying.
        # Given the queue likely won't be massive (hundreds, maybe thousands), 
        # sorting on retrieval or extraction might be acceptable, 
        # OR we just re-calculate scores when we need to pop.
        
        # For a truly dynamic score = bid + (now - timestamp) * weight
        # score = bid + now*weight - timestamp*weight
        # score = (bid - timestamp*weight) + now*weight
        # Since now*weight is common to all items, we can just order by (bid - timestamp*weight).
        # Let's call this "base_score".
        # The item with the HIGHEST base_score will always have the HIGHEST current score.
        
        # We use a min-heap with negated base_score to get the max.
        base_score = bid - (timestamp * self.time_weight)
        
        # Store as (-base_score, timestamp, bid, soundcloud_id)
        # We include timestamp to break ties (FIFO if scores match exactly, though float logic makes that rare)
        # If base_scores are equal, lower timestamp (older) should come first.
        # In a min-heap, (-base_score) being equal, the next item is timestamp.
        # Smaller timestamp is earlier time. So this works perfectly.
        
        item = (-base_score, timestamp, bid, soundcloud_id)
        heapq.heappush(self.queue, item)
        print(f"Added song {soundcloud_id} with bid {bid}. Base score: {base_score:.4f}")

    def get_next_song(self) -> Optional[dict]:
        """
        Extracts the next song to play.
        """
        if not self.queue:
            return None
            
        # Pop the highest priority item
        neg_base_score, timestamp, bid, soundcloud_id = heapq.heappop(self.queue)
        
        # Calculate final effective score for display/logging
        now = time.time()
        wait_time = now - timestamp
        final_score = bid + (wait_time * self.time_weight)
        
        return {
            "soundcloud_id": soundcloud_id,
            "bid": bid,
            "wait_time": wait_time,
            "final_score": final_score
        }

    def get_queue_status(self) -> List[dict]:
        """
        Returns the current state of the queue sorted by priority, without removing items.
        Useful for frontend display.
        """
        # We need to sort a copy of the queue
        # The heap structure is not necessarily sorted list.
        sorted_queue = sorted(self.queue, key=lambda x: (x[0], x[1]))
        
        results = []
        now = time.time()
        
        for neg_base_score, timestamp, bid, soundcloud_id in sorted_queue:
            wait_time = now - timestamp
            final_score = bid + (wait_time * self.time_weight)
            results.append({
                "soundcloud_id": soundcloud_id,
                "bid": bid,
                "wait_time": wait_time,
                "final_score": final_score
            })
            
        return results
