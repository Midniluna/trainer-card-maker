$(".fa-star").on("click", async function (evt) {
	evt.preventDefault();

    const pkmnID = $(this).attr("data-userpkmn-id")
    console.log(`Clicked! ID = ${pkmnID}`)
    await axios.patch(`${BASE_URL}/${pkmnID}/fave`)
    $(this).toggleClass('fa-regular')
    $(this).toggleClass('fa-solid')
})