
from django.conf import settings
import json
import os.path
import gzip
import pickle

def init():
    cache_folder = settings.CACHE_PATH
    if not os.path.isdir(cache_folder):
        os.mkdir(cache_folder)

def get_from_cache(id):

    data = None
    #cache_folder = current_app.config['CACHE_PATH']
    cached_file = os.path.join(settings.CACHE_PATH, str(id) + ".pkl")
    if os.path.isfile(cached_file):
        #with gzip.open(cached_file, "rt", encoding="utf-8") as f:
        #    data = json.load(f)
        #    print("\ngot from cache:"+id)
        #f.close()
        with open(cached_file, 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            data = pickle.load(f)

    return data

def add_to_cache(id, data):
    #cache_folder = current_app.config['CACHE_PATH']
    cached_file = os.path.join(settings.CACHE_PATH, str(id) + ".pkl")

    #with gzip.open(cached_file, "wt", encoding="utf-8") as f:
    #    json.dump(data,f)
    #f.close()
    with open(cached_file, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)