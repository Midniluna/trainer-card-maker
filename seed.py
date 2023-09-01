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
        species = pokemon["name"]
        is_legendary = bool(req["is_legendary"])
        is_mythical = bool(req["is_mythical"])

        for variant in req["varieties"]:

            # name and url changes depending on variant
            variant_name = variant["pokemon"]["name"]
            url = variant["pokemon"]["url"]

            ###### I just realized I need to do ANOTHER API call to get the sprite. This seed is going to take a hot minute but at least it'll make the app faster in the long run :sob emoji: ######
            get_sprite = requests.get(url)
            sprite_req = get_sprite.json()

            sprite = sprite_req["sprites"]["front_default"]

            if not sprite:
                # If there's no default sprite, there won't be a shiny sprite, no need to check for both
                print("""
                    -----------------------
                      NO SPRITES AVAILABLE
                      SKIP POKEMON
                    -----------------------""")
            else:
                # add pokemon to list

                shiny_sprite = sprite_req["sprites"]["front_shiny"]
                # If there's a shiny sprite, include it, else None
                if not shiny_sprite:
                    shiny_sprite = None

                new_mon = Pokemon(species=species, species_dexnum = dexnum,     variant_name = variant_name, is_legendary = is_legendary,   is_mythical = is_mythical, sprite = sprite, shiny_sprite =    shiny_sprite, url = url)
                db.session.add(new_mon)
                db.session.commit()
                print(f'species: {new_mon.species} variant: {new_mon.variant_name}  id: {new_mon.id}; ADDED')
                print(f"Sprites: {sprite} ------------ {shiny_sprite}")


get_all_pkmn()