$slot1 = $(".pokemon-container[data-slot-index='slot1']")
$slot2 = $(".pokemon-container[data-slot-index='slot2']")
$slot3 = $(".pokemon-container[data-slot-index='slot3']")
$slot4 = $(".pokemon-container[data-slot-index='slot4']")
$slot5 = $(".pokemon-container[data-slot-index='slot5']")
$slot6 = $(".pokemon-container[data-slot-index='slot6']")

// I could call to the SQL database, but I want to show that I'm able to do API calls as well. Perhaps less efficient? Can adjust to SQL calls later
$(".pokemon-list-form").on("submit", async function (evt) {
    evt.preventDefault();
    $target = $(this).parent();
    console.log($target);

    localCard = undefined

    if (window.localStorage.getItem('localCard') != null) {
        localCard = JSON.parse(localStorage.getItem('localCard'));
        // It works
        console.log(`Slot 1 contents: ${localCard.slot1}`)
    } else {
        new_card = {
            slot1 : "",
            slot2 : "",
            slot3 : "",
            slot4 : "",
            slot5 : "",
            slot6 : "",
        }
        localCard = localStorage.setItem('localCard', JSON.stringify(new_card));
    }

    // Making sure all values are returning as expected
    slot = $target.attr("data-slot-index");
    console.log(slot);
    pkmnURL = $target.attr("data-pokemon-url");
    console.log(pkmnURL);
    value = $target.find("select").val();
    console.log(value);

    let response = await axios.get(value);

    pokemon = response.data.name
    sprite = response.data.sprites.front_default
    console.log(pokemon)
    console.log(sprite)

})