const SLOTLIST = ['slot1', 'slot2' ,'slot3', 'slot4', 'slot5', 'slot6']

function initiateLocalcard() {
    // if localCard does not exist in localstorage, make it.
    if (window.localStorage.getItem('localCard') !== null) {
        return;
    } else {
        new_card = {
            slot1 : "",
            slot2 : "",
            slot3 : "",
            slot4 : "",
            slot5 : "",
            slot6 : "",
        }
        window.localStorage.setItem('localCard', JSON.stringify(new_card));
    };
}

initiateLocalcard();

function append_pokemon(type) {
    for (let i = 0; i < SLOTLIST.length; i++) {
        // Iterate over pokemon stored in localCard and apply existing pokemon onto DOM
    
        let slotKey = SLOTLIST[i]
        let $targetDiv = $(`.${type}[data-slot-index='${slotKey}']`)
        let cardObj = JSON.parse(window.localStorage.getItem('localCard'))
    
        if (cardObj[slotKey] !== "") {
            let url = cardObj[slotKey]["url"]
            let nickname = cardObj[slotKey]["nickname"]
            let sprite = cardObj[slotKey]["sprite"]
            let species = cardObj[slotKey]["species"]
    
            if (nickname !== "") {
                $targetDiv.find(".nickname").text(nickname)
            }
            else {
                $targetDiv.find(".nickname").text("----")
            }
    
            $targetDiv.find("img").attr("src", sprite)
            $targetDiv.find(".species").text(species)
            $targetDiv.attr("data-pokemon-url", url)
    
            // we also want to default the input values to match the provided pokemons' values
            $targetDiv.find("select").val(url);
            $targetDiv.find("#nickname").val(nickname);
        } 
        // If pokemon doesn't exist in given slot, ignore it
        // Correction: make sure it appends the default image
        else {
            $targetDiv.find("img").attr("src", "/static/images/no-symbol.png")
            $targetDiv.find(".species").text("No pokemon")
            $targetDiv.find(".nickname").text("----")
            $targetDiv.find("#nickname").val("")
        }
    }

}

append_pokemon("saved");
append_pokemon("local");





// ------------------------------------------




// I want the localstorage to look like this (url acts like an id): 
// { 'slot1' : 
    // { 'url' : 'https:pokeapi.co/api/v2/pokemon/id',
    //   'sprite' : 'something.png',
    //   'species' : 'species',
    //   'nickname' : 'Nickname'
    // } ,
    // 'slot2' : etc
// }

// I could call to the SQL database, but I want to show that I'm able to do API calls as well. Perhaps less efficient? Can adjust to SQL calls later
$(".pokemon-list-form").on("submit", async function (evt) {
    evt.preventDefault();
    const $TARGET = $(this).parent();
    
    
    let cardObj = JSON.parse(window.localStorage.getItem('localCard'));
    
    let selection = $TARGET.find("select").val();
    let slot = $TARGET.attr("data-slot-index");
    
    // If they select the "NONE" pokemon, clear all data for that slot

    if (selection == "") {
        // clear data from slot in localstorage
        cardObj[slot] = "";
        window.localStorage.setItem('localCard', JSON.stringify(cardObj));
        // then reset slot to default on DOM
        $TARGET.find("img").attr("src", "/static/images/no-symbol.png");
        $TARGET.find(".species").text("No pokemon")
        $TARGET.attr("data-pokemon-url", "");
        $TARGET.find(".nickname").text("----");
        $TARGET.find("#nickname").val("");
        return;
    } 

    // Otherwise, append selected pokemon to DOM
    else {
        let response = await axios.get(selection);
        
        let nickname = $TARGET.find("#nickname").val();
        let pokemon = response.data.name;
        pokemon = capitalize(pokemon)
        let sprite = response.data.sprites.front_default;
        
        cardObj[slot] = {
            "url" : selection,
            "sprite" : sprite,
            "species" : pokemon,
            "nickname" : nickname
        };
        
        window.localStorage.setItem('localCard', JSON.stringify(cardObj));
    
        $TARGET.find("img").attr("src", sprite);
        $TARGET.find(".species").text(pokemon);
        $TARGET.attr("data-pokemon-url", selection);
    
        if (nickname !== "") {
            $TARGET.find(".nickname").text(nickname);
        }
        else {
            $TARGET.find(".nickname").text("----");
        }
    }
    
})



$(".pokemon-search-form").on("submit", async function (evt) {
    evt.preventDefault();
    const $TARGET = $(this).find("#search");
    const $APPENDRESULTS = $(".search-results")
    let input = $TARGET.val()
    $APPENDRESULTS.empty()

    if (input == "") {
        return
    }

    let response = await axios.post(`${BASE_URL}/search-pokemon`, {
        input
    });

    result_pkmn = response.data
    pkmn_names = Object.keys(result_pkmn)

    pkmn_names.forEach((pokemon) => {
        let dexnum = result_pkmn[pokemon]["dexnum"]
        let sprite = result_pkmn[pokemon]["sprite"]
        $APPENDRESULTS.append(`
        <div class="pokemon-container search" style="text-align: center;">
		<img
		src="${sprite}"
		alt=""
		class="pokemon-image"
		/>
		<span style="display: block"><b>Name:</b> ${capitalize(pokemon)}</span>
		<span style="display: block"><b>Dex number</b>: #${dexnum}</span>
        `)
    });
})

// Reminder to self; [x or None] in python is the same as 
//                   [x ? x : null] in js