API being used:
PokeAPI ( https://pokeapi.co/ )

There is a section in the generate.html file (an <h4> element) that displays the pokemon's name on the DOM in case you aren't very familiar with pokemon and want an easy catch. If you're looking for more of a challenge, comment it out before generating your pokemon!

The "reset" option in the '/generate' route will also not be available to most users because there will be a daily lockout, and if you'd like to test that daily lockout you may comment out the route and/or reset form on the generate.html page, but be warned you WILL be locked out unless you mess around with your last_genned (and/or) last_caught data in ipython or the like!

If you want to have a little fun and guarantee yourself a shiny, read line 303 on the app.py file!