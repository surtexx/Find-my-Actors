import requests
import os
from multiprocessing import Pool
import uuid
from dotenv import load_dotenv


def configure():
    load_dotenv()


def download_images(search_term, num_images):
    url = 'https://api.bing.microsoft.com/v7.0/images/search'
    params = {
        'q': search_term,
        'count': num_images,
        'license': 'Any',
        'imageType': 'photo',
        'imageContent': 'Portrait',
        'mkt': 'en-US',
    }
    headers = {
        'Ocp-Apim-Subscription-Key': os.getenv('api-key')
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        cwd = os.getcwd()
        cwd = os.path.join(cwd, 'images')
        targetPath = os.path.join(cwd, search_term.lower() + "1")
        if not os.path.exists(targetPath):
            os.mkdir(targetPath)

            data = response.json()

            for i, result in enumerate(data['value']):
                image_url = result['contentUrl']
                filename = str(uuid.uuid1()) + ".jpg"

                response = requests.get(image_url, stream=True)
                filename = os.path.join(targetPath, filename)
                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)

                print(f'Successfully downloaded image {i + 1} as {filename}')

                if i + 1 == num_images:
                    break
        else:
            print(f'Images with actor {search_term} already exist. Skipping download.')
    else:
        print(f'Failed to fetch images with actor {search_term}. Eror code {response.status_code}')


if __name__ == '__main__':
    configure()
    num_images = 60
    actors = os.getenv('actors').split("  ")

    with Pool(2) as p:
        p.starmap(download_images, [(actor, num_images) for actor in actors])
