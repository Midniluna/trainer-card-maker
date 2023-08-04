import requests

from app import db, app
from models import Pokemon


app.app_context().push()

db.drop_all()
db.create_all()



def get_all_pkmn():
    """Push basic data for all pokemon into database"""
    data = requests.get('https://pokeapi.co/api/v2/pokemon-species?limit=100000&offset=0')
    r = data.json()
    r = r["results"]
    
    # Now turn pokemon list into every pokemon, INCLUDING regional variants and megas/gmax formes. A bit time consuming to put all in database, BUT WAY less time consuming to reach into the database than to make an API request for every single pokemon. There are a lot of pokemon lol.

    for pokemon in r:
        single_poke = requests.get(pokemon["url"])
        req = single_poke.json()
        # Dex number will always be the same for same-species, regardless of variant
        dexnum = req["pokedex_numbers"][0]["entry_number"]

        for variant in req["varieties"]:

            # name and url changes depending on variant
            name = variant["pokemon"]["name"]
            url = variant["pokemon"]["url"]

            # add pokemon to list
            new_mon = Pokemon(species_dexnum = dexnum, name = name, url = url)
            db.session.add(new_mon)
            db.session.commit()
            print(f'pokemon: {new_mon.name} id: {new_mon.id}; ADDED')


get_all_pkmn()