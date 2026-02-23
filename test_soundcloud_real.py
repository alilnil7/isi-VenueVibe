from soundcloud_client import soundcloud_client

def test_real_resolve():
    url = "https://soundcloud.com/forss/flickermood"
    print(f"Resolving {url}...")
    track = soundcloud_client.resolve_track(url)
    if track:
        print(f"Resolved: {track}")
        assert track['id'] == "296803" # ID of flickermood
        assert track['title'] == "Flickermood"
        print("Real SoundCloud resolution working!")
    else:
        print("Failed to resolve track.")

if __name__ == "__main__":
    test_real_resolve()
