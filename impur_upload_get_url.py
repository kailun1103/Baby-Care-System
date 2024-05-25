from imgurpython import ImgurClient
import time

if __name__ == "__main__":
    # client = ImgurClient(imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token)
    client = ImgurClient("a0aef3d206a9405", "b5c854b59f60a5daaeb29bf2cb1ada3d00393fe1", "31e29ec2770045828bdf07af121b31fe8a383c6d", "1693d87de9af67966b246a03139c0d6238efeb71")
    config = {
        'album': "kailun1103",
        'name': 'test-name!',
        'title': 'test-title',
        'description': 'test-description'
    }
    print("Uploading image... ")
    image = client.upload_from_path('20240525_033222.jpg', anon=False)
    print(image)
    time.sleep(5)
    image_link = image['link']
    print(f"Uploaded image ID: {image_link}")