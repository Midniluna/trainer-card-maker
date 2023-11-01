const SLOTLIST = ['slot1', 'slot2' ,'slot3', 'slot4', 'slot5', 'slot6']

function initiateLocalcard() {
    // if localCard does not exist in localstorage, make it.
    if (window.localStorage.getItem('localCard') !== null) {
        return;
    } else {
        const NEW_CARD = {
            slot1 : "",
            slot2 : "",
            slot3 : "",
            slot4 : "",
            slot5 : "",
            slot6 : "",
        }
        window.localStorage.setItem('localCard', JSON.stringify(NEW_CARD));
    };
}

initiateLocalcard();

function append_pokemon(type) {
    for (let i = 0; i < SLOTLIST.length; i++) {
        // Iterate over pokemon stored in localCard and apply existing pokemon onto DOM
    
        const SLOT_KEY = SLOTLIST[i]
        const $TARGET_DIV = $(`.${type}[data-slot-index='${SLOT_KEY}']`)
        const CARD_OBJ = JSON.parse(window.localStorage.getItem('localCard'))
    
        if (CARD_OBJ[SLOT_KEY] !== "") {
            const URL = CARD_OBJ[SLOT_KEY]["url"]
            const NICKNAME = CARD_OBJ[SLOT_KEY]["nickname"]
            const SPRITE = CARD_OBJ[SLOT_KEY]["sprite"]
            const SPECIES = CARD_OBJ[SLOT_KEY]["species"]
    
            if (NICKNAME !== "") {
                $TARGET_DIV.find(".nickname").text(NICKNAME)
            }
            else {
                $TARGET_DIV.find(".nickname").text("----")
            }
    
            $TARGET_DIV.find("img").attr("src", SPRITE)
            $TARGET_DIV.find(".species").text(SPECIES)
            $TARGET_DIV.attr("data-pokemon-url", URL)
    
            // we also want to default the input values to match the provided pokemons' values
            $TARGET_DIV.find("select").val(URL);
            $TARGET_DIV.find("#nickname").val(NICKNAME);
        } 
        // If pokemon doesn't exist in given slot, make sure it appends the default image
        else {
            $TARGET_DIV.find("img").attr("src", "/static/images/no-symbol.png")
            $TARGET_DIV.find(".species").text("No pokemon")
            $TARGET_DIV.find(".nickname").text("----")
            $TARGET_DIV.find("#nickname").val("")
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
    
    
    const CARD_OBJ = JSON.parse(window.localStorage.getItem('localCard'));
    
    const SELECTION = $TARGET.find("select").val();
    const SLOT = $TARGET.attr("data-slot-index");
    
    // If they select the "NONE" pokemon, clear all data for that slot

    if (SELECTION == "") {
        // clear data from slot in localstorage
        CARD_OBJ[SLOT] = "";
        window.localStorage.setItem('localCard', JSON.stringify(CARD_OBJ));
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
        const RESP = await axios.get(SELECTION);
        
        const NICKNAME = $TARGET.find("#nickname").val();
        let pokemon = RESP.data.name;
        pokemon = capitalize(pokemon)
        const SPRITE = RESP.data.sprites.front_default;
        
        CARD_OBJ[SLOT] = {
            "url" : SELECTION,
            "sprite" : SPRITE,
            "species" : pokemon,
            "nickname" : NICKNAME
        };
        
        window.localStorage.setItem('localCard', JSON.stringify(CARD_OBJ));
    
        $TARGET.find("img").attr("src", SPRITE);
        $TARGET.find(".species").text(pokemon);
        $TARGET.attr("data-pokemon-url", SELECTION);
    
        if (NICKNAME !== "") {
            $TARGET.find(".nickname").text(NICKNAME);
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
    let INPUT = $TARGET.val()
    $APPENDRESULTS.empty()

    if (INPUT == "") {
        return
    }

    const RESP = await axios.post(`${BASE_URL}/search-pokemon`, {
        input : INPUT.toLowerCase()
    });

    const RESLT_PKMN = RESP.data
    const PKMN_NAMES = Object.keys(RESLT_PKMN)

    PKMN_NAMES.forEach((pokemon) => {
        const DEXNUM = RESLT_PKMN[pokemon]["dexnum"]
        const SPRITE = RESLT_PKMN[pokemon]["sprite"]
        $APPENDRESULTS.append(`
        <div class="pokemon-container search" style="text-align: center;">
		<img
		src="${SPRITE}"
		alt=""
		class="pokemon-image"
		/>
		<span style="display: block"><b>Name:</b> ${capitalize(pokemon)}</span>
		<span style="display: block"><b>Dex number</b>: #${DEXNUM}</span>
        `)
    });
})

// Reminder to self; [x or None] in python is the same as 
//                   [x ? x : null] in js