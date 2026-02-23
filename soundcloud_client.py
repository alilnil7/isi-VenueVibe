import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SoundCloudClient:
    def __init__(self):
        # Using a common public client_id for SoundCloud API v2
        self.client_id = os.getenv("SOUNDCLOUD_CLIENT_ID", "iZIs9mchV9lx8H3p7N78fS_kH7K374pG")
        self.resolve_url = "https://api-v2.soundcloud.com/resolve"

    def resolve_track(self, url: str):
        """
        Resolves a SoundCloud URL to track metadata using SoundCloud v2 API.
        """
        try:
            params = {
                "url": url,
                "client_id": self.client_id
            }
            response = requests.get(self.resolve_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant metadata
            return {
                "id": str(data.get('id')),
                "title": data.get('title'),
                "user": {"username": data.get('user', {}).get('username')},
                "duration": data.get('duration', 0) # Duration is already in ms in v2 API
            }
        except Exception as e:
            print(f"Error resolving SoundCloud track: {e}")
            return None

soundcloud_client = SoundCloudClient()
