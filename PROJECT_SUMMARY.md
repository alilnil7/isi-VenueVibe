# Isi-VenueVibes — Project Summary for AI Agents

## Project Overview

**Isi-VenueVibes** is a university project (3rd year — *Integración de Sistemas Informáticos*) that implements the back-end engine for a **music promotion platform for live venues**.

The core concept: songs submitted by venue visitors are queued and played in order. Song priority is determined by a **monetary bid** the submitter pays, combined with a **fairness boost** based on how long a song has been waiting in the queue. This prevents a high bidder from monopolously blocking other songs indefinitely.

---

## Repository Structure

```
Isi-VenueVibes/
├── engine.py          # Core MusicQueue implementation (main logic)
├── Core_Engine.py     # Placeholder / future core engine file (currently empty)
└── test_queue.py      # Manual/unit tests for MusicQueue
```

---

## File Descriptions

### `engine.py` — Music Queue Engine
The only implemented module. Contains two classes:

#### `QueueItem` (dataclass)
A data container representing a song entry in the queue.

| Field | Type | Description |
|---|---|---|
| `score` | `float` | Sorting score (used for heap ordering) |
| `timestamp` | `float` | Unix time when the song was added |
| `bid` | `float` | Monetary bid placed by the submitter |
| `soundcloud_id` | `str` | Unique SoundCloud track identifier |

> **Note:** `QueueItem` is defined but the actual heap stores raw tuples, not `QueueItem` instances.

#### `MusicQueue`
The main queue manager. Internally uses a **min-heap** (`heapq`) with a negated score to simulate a max-heap.

**Key design decision — dynamic scoring without re-heapifying:**
Instead of re-scoring every item on every tick, the engine uses a mathematical invariant:

```
current_score(t) = bid + (t - timestamp) * time_weight
                 = (bid - timestamp * time_weight) + t * time_weight
```

Since `t * time_weight` is the same for all items at any given moment `t`, ranking is preserved by only storing `base_score = bid - timestamp * time_weight`. This allows O(log n) inserts and O(log n) pops without ever needing to rebuild the heap.

**Methods:**

| Method | Description |
|---|---|
| `add_song(soundcloud_id, bid)` | Adds a song to the priority queue |
| `get_next_song()` | Pops and returns the highest-priority song as a `dict` |
| `get_queue_status()` | Returns all current queue items sorted by priority (non-destructive) |

**Return shape of `get_next_song()` / `get_queue_status()` items:**
```python
{
    "soundcloud_id": str,   # SoundCloud track ID
    "bid": float,            # Original bid in currency units
    "wait_time": float,      # Seconds spent in queue
    "final_score": float     # Effective score at retrieval time
}
```

**Configurable parameter:**
- `time_weight` (default: `0.01 / 60` ≈ 0.000167 per second) — how many bid-equivalent currency units are added per second of waiting. At default, a song gains ~$0.01 per minute of waiting.

---

### `Core_Engine.py` — Placeholder
Currently **empty**. Likely intended to contain a higher-level orchestrator or integration layer that connects `MusicQueue` to external services (SoundCloud API, payment systems, venue management, etc.).

---

### `test_queue.py` — Tests
A standalone test script that validates the fairness behavior of `MusicQueue`.

**Test scenario:**
1. Add `song_A` with bid `10.0`.
2. Sleep 2 seconds.
3. Add `song_B` with bid `10.5`.
4. With `time_weight = 0.5/s`, `song_A`'s score ≈ 11.0, `song_B`'s score ≈ 10.5.
5. **Assert** `song_A` is popped first despite the lower bid.
6. **Assert** `song_B` is popped second.

Run with:
```bash
python test_queue.py
```

---

## Current State & Known Gaps

| Area | Status |
|---|---|
| Priority queue logic | ✅ Implemented & tested |
| Fairness (time boost) | ✅ Implemented via `base_score` invariant |
| `Core_Engine.py` | ❌ Empty — not yet implemented |
| SoundCloud API integration | ❌ Not present |
| Payment / bid processing | ❌ Not present |
| REST API / web layer | ❌ Not present |
| Persistence (DB/storage) | ❌ Not present |

---

## Key Algorithms & Concepts

- **Data structure:** Binary min-heap (`heapq`) storing tuples `(-base_score, timestamp, bid, soundcloud_id)`
- **Tie-breaking:** If two songs have identical `base_score`, the one with the earlier `timestamp` (older) wins (natural tuple ordering on the second element).
- **Time complexity:** `add_song` → O(log n), `get_next_song` → O(log n), `get_queue_status` → O(n log n)
- **Space complexity:** O(n)

---

## Dependencies

| Library | Purpose |
|---|---|
| `heapq` | Priority queue (stdlib) |
| `time` | Timestamps (stdlib) |
| `dataclasses` | `QueueItem` definition (stdlib) |
| `typing` | Type hints (stdlib) |

No external (pip) dependencies are currently required.
