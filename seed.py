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
    

    for pokemon in r:

        single_poke = requests.get(pokemon["url"])
        req = single_poke.json()

        # Get the dex number from the national pokedex
        dexnum = req["pokedex_numbers"][0]["entry_number"]
        # Get the url of the default form/regional variant
        url = req["varieties"][0]["pokemon"]["url"]
        new_mon = Pokemon(species_dexnum = dexnum, name = pokemon["name"], url = url)
        db.session.add(new_mon)
        db.session.commit()
        print(f'pokemon: {new_mon.name} id: {new_mon.id}; ADDED')

        # If the pokemon has multiple forms, add the other forms to the choices
        if len(req["varieties"]) > 1:
            for forme in req["varieties"]:
                if forme["is_default"]:
                    return
                else:
                    # dex number is the same since it's the same species. variant name and url are different.
                    forme = Pokemon(species_dexnum = dexnum, name = forme["pokemon"]["name"], url = forme["pokemon"]["url"])
                    db.session.add(forme)
                    db.session.commit()
                    print(f'pokemon: {forme.name} id: {forme.id}; ADDED')
            return

# Hang on.




get_all_pkmn()