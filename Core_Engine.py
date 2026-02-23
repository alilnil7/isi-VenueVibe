import os
from dotenv import load_dotenv
from engine import MusicQueue
from models import SessionLocal, SongEntry, Transaction, init_db
from soundcloud_client import soundcloud_client
from stripe_client import stripe_client

load_dotenv()

class CoreEngine:
    def __init__(self):
        self.music_queue = MusicQueue()
        self.music_queue.time_weight = float(os.getenv("TIME_WEIGHT", 0.000167))
        init_db()

    def submit_song(self, url: str, bid: float):
        """
        Processes a song submission: resolves meta, creates DB record, returns payment session.
        """
        track_info = soundcloud_client.resolve_track(url)
        if not track_info:
            raise ValueError("Could not resolve SoundCloud URL")

        db = SessionLocal()
        try:
            # Create song entry if not exists or just link to it
            song = db.query(SongEntry).filter(SongEntry.soundcloud_id == track_info['id']).first()
            if not song:
                song = SongEntry(
                    soundcloud_id=track_info['id'],
                    title=track_info.get('title'),
                    artist=track_info.get('user', {}).get('username'),
                    duration=track_info.get('duration')
                )
                db.add(song)
                db.commit()
                db.refresh(song)

            # Create pending transaction
            session_id = stripe_client.create_checkout_session(
                soundcloud_id=track_info['id'],
                amount=bid,
                success_url="http://localhost:8000/success",
                cancel_url="http://localhost:8000/cancel"
            )

            transaction = Transaction(
                song_id=song.id,
                bid_amount=bid,
                stripe_session_id=session_id,
                status="pending"
            )
            db.add(transaction)
            db.commit()

            return session_id
        finally:
            db.close()

    def confirm_payment(self, stripe_session_id: str):
        """
        Confirms payment and adds song to the live music queue.
        """
        db = SessionLocal()
        try:
            txn = db.query(Transaction).filter(Transaction.stripe_session_id == stripe_session_id).first()
            if txn and txn.status == "pending":
                txn.status = "completed"
                song = db.query(SongEntry).filter(SongEntry.id == txn.song_id).first()
                self.music_queue.add_song(song.soundcloud_id, txn.bid_amount)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def get_queue(self):
        return self.music_queue.get_queue_status()

    def pop_next(self):
        return self.music_queue.get_next_song()

core_engine = CoreEngine()
