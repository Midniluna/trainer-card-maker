const BASE_URL = 'https://pokepals-trainercard-maker.onrender.com'

function capitalize(str){
	return str.charAt(0).toUpperCase() + str.slice(1);
}


// Used to submit user's attempt to catch a pokemon

$("#guess-pokemon-form").on("submit", async function (evt) {
	evt.preventDefault();

	// Clear the error message contents + hide the error message element
	$("#alert-guess-mon").empty();

	// remove any previous error message styling
	if ($("#alert-guess-mon").hasClass("alert-danger")) {
		$("#alert-guess-mon").toggleClass("alert-danger");
	}
	if ($("#alert-guess-mon").hasClass("alert-success")) {
		$("#alert-guess-mon").toggleClass("alert-success");
	}

	let species = "";

	const $GENNED = $(".genned-mon").closest("div");
	const GENNED_ID = $GENNED.attr("data-genned-id");
	const USER_ID = $GENNED.attr("data-user-id");

	if ($("#species").val() !== "") {
		species = $("#species").val().toLowerCase();

		const RESP = await axios.post(`${BASE_URL}/catch/${GENNED_ID}`, {
			species,
		});

		if (RESP.data === null) {
			return;
		} else if (RESP.data === "Failed") {
			$("#species").val() == "";

			// error message content is always cleared at the start, so always re-append error when catch-attempt is failed
			$("#alert-guess-mon")
				.css("display", "block")
				.toggleClass("alert-danger")
				.append(`<p>That is the incorrect pokemon. Check your spelling!</p>`);
		} else if (RESP.data === "Success") {
			$("#species").val() == "";
			// window.location.replace("http://localhost:5000/home");
			$(".genned-mon-content").empty();
			$(".alert").empty();
			$("#alert-guess-mon")
				.toggleClass("alert-success")
				.css("display", "block")
				.append(`<p>Congrats! You've caught a(n) ${species}! Would you like to name it? <a href='profile/${USER_ID}/edit/${GENNED_ID}'>[Yes]</a></p>`);
			
			$(".redirect").append(`
            <br>
            <a href="/home" class="btn btn-lg">Return Home</a>`);
		}
	}

	return;
});

$(".hint-btn").on("click", function(evt) {
	evt.preventDefault()

	const SHOW_HINT = $(this).siblings(".show-hint");
	
	if (SHOW_HINT.css('display') != 'none') {
		return;
	}
	else {
		let species = $(this).attr("data-species-name");
		species = capitalize(species);
		console.log(species)
		
		// If the pokemon's name is only 6 or less letters long, show the first 3 letters. Else, show the first 4
		let visible = 0
		// species.slice(0, 4)
		if (species.length <= 6) {
			visible = 3;
		}
		else {
			visible = 4;
		}
		
		hint = species.slice(0, visible);
		numsToHide = species.length - hint.length
		for ( i = 0; i < numsToHide; i++) {
			hint += '_'
		}

		
		SHOW_HINT.text(hint);
		SHOW_HINT.css('display', 'inline');
	}

})

$(".fa-star").on("click", async function (evt) {
	evt.preventDefault();
	console.log("clicked")

    const PKMN_ID = $(this).attr("data-userpkmn-id")
	const USER_ID = $(this).attr("data-user-id")
    await axios.patch(`${BASE_URL}/${PKMN_ID}/fave`, {user_id : USER_ID})
    $(this).toggleClass('fa-regular')
    $(this).toggleClass('fa-solid')
})


// --------------------------------------------------------


// This is to allow user to edit their card

$(".select-slot").on("click", async function (evt) {
	evt.preventDefault();
	const $TARGET = $(this)

	const $ACTIVE = $(".active");

	// If there are no selected buttons, let user select
	if ($ACTIVE.length === 0) {
		$TARGET.toggleClass("active");
	} 

	else if ($ACTIVE.length === 1) {
		// if target is the "active" button, deselect
		if ($TARGET.hasClass("active")) {
			$TARGET.toggleClass("active");
		}
		// If user selects one slot and then another slot, swap the pokemons' positions
		else {
			const SLOT = $ACTIVE.attr("data-slot-id")
			const SLOT2 = $TARGET.attr("data-slot-id")
			const PKMN_ID = $ACTIVE.attr("data-userpkmn-id")
			const PKMN2_ID = $TARGET.attr("data-userpkmn-id")
			const USER_ID = $(".card-container").attr("data-user-id")

			await axios.patch(`${BASE_URL}/card/edit/${USER_ID}/submit`, {
				slot : SLOT,
				slot2 : SLOT2,
				pkmn_id : PKMN_ID,
				pkmn2_id : PKMN2_ID,
			})

			// Swap pokemon data on DOM

			const $IMG = $ACTIVE.parent().find(".pokemon-image");
			const $NICKNAME = $ACTIVE.parent().find(".nickname");
			const $SPECIES = $ACTIVE.parent().find(".species");
			const $ID = $ACTIVE.parent().find(".pkmnID");

			const $IMG_2 = $TARGET.parent().find(".pokemon-image");
			const $NICKNAME_2 = $TARGET.parent().find(".nickname");
			const $SPECIES_2 = $TARGET.parent().find(".species");
			const $ID_2 = $TARGET.parent().find(".pkmnID")

			// Save data from first slot to append to second slot and vice versa
			// These values aren't redeclared later but it looks easier to read if I leave these as let.
			// There's definitely a more efficient way to do this but I'll look into how to do that a bit later
			let swapimg = $IMG.attr("src")
			let swapnickname = $NICKNAME.text()
			let swapspecies = $SPECIES.text()
			let swapid =  $ID.text()

			let swapimg2 = $IMG_2.attr("src")
			let swapnickname2 = $NICKNAME_2.text()
			let swapspecies2 = $SPECIES_2.text()
			let swapid2 =  $ID_2.text()
			
			// Fill first slot's data with data from second slot
			$IMG.attr("src", swapimg2);
			$NICKNAME.text(swapnickname2);
			$SPECIES.text(swapspecies2);
			$ID.text(swapid2)
			$ACTIVE.attr("data-userpkmn-id", PKMN2_ID)

			// Now fill second slot's data with data from first slot
			$IMG_2.attr("src", swapimg);
			$NICKNAME_2.text(swapnickname);
			$SPECIES_2.text(swapspecies);
			$ID_2.text(swapid)
			$TARGET.attr("data-userpkmn-id", PKMN_ID)

			$ACTIVE.toggleClass("active");
		}
	}
	return
})



$(".select-mon").on("click", async function (evt) {
	evt.preventDefault();
	const $TARGET = $(this)
	const $ACTIVE = $(".active");

	if ($ACTIVE.length === 0) {
		// if none selected, don't do anything
		console.log("None selected")
		return
	}
	else {
		
		const SLOT = $ACTIVE.attr("data-slot-id")
		const PKMN_ID = $TARGET.attr("data-userpkmn-id")
		const USER_ID = $(".card-container").attr("data-user-id")
		
		
		// Check through list of userpkmn ids currently in card and confirm selected pokemon's id is not a perfect match to any of them
		const ID_LIST = []

		$(".select-slot").each(function() {
			let id = $(this).attr("data-userpkmn-id")
			ID_LIST.push(parseInt(id))
		})
			if (ID_LIST.includes(parseInt(PKMN_ID)) ) {
				return
			}
			
			// Otherwise, display new pokemon on screen.
			else {
				
				// Tell python slots are not being swapped. Swaps only happen on .select-slot buttons
				const SLOT2 = "None" 
				const PKMN2_ID = "None" 

				const IMG = $ACTIVE.parent().find(".pokemon-image");
				const NICKNAME = $ACTIVE.parent().find(".nickname");
				const SPECIES = $ACTIVE.parent().find(".species");
				const ID = $ACTIVE.parent().find(".pkmnID");
				
				// Append delete button if adding a pokemon into a blank slot
				const $DELETE_BTN = $(`<button class="btn btn-danger" data-slot-id="${SLOT}">Remove</button>`)
				
				// If there's 
				if (SPECIES.text() == "No pokemon") {
					$ACTIVE.parent().find("span.delete-slot").append($DELETE_BTN);
				}
				
				const RESP = await axios.post(`${BASE_URL}/card/edit/${USER_ID}/submit`, {
					slot : SLOT,
					slot2 : SLOT2,
					pkmn_id : PKMN_ID,
					pkmn2_id : PKMN2_ID,
				});
				
				IMG.attr("src", RESP.data.sprite);
				NICKNAME.text(`${RESP.data.nickname}`);
				SPECIES.text(`${RESP.data.species}`);
				ID.text(`ID: #${PKMN_ID}`);
				$ACTIVE.attr("data-userpkmn-id", PKMN_ID)
				
				$ACTIVE.toggleClass("active")
				

			}
			

	}
	return
})

// class="btn btn-danger delete-slot" data-slot-id="{{slot}}"


$(".delete-slot").on("click", async function (evt) {
	evt.preventDefault();
	const $TARGET = $(this).siblings(".select-slot")
	
	const SLOT_ID = $TARGET.attr("data-slot-id")
	const USER_ID = $(".card-container").attr("data-user-id")

	const IMG = $TARGET.parent().find(".pokemon-image");
	const NICKNAME = $TARGET.parent().find(".nickname");
	const SPECIES = $TARGET.parent().find(".species");
	const ID = $TARGET.parent().find(".pkmnID");

	IMG.attr("src", `${BASE_URL}/static/images/no-symbol.png`);
	NICKNAME.text("(nickname)");
	SPECIES.text("No pokemon");
	ID.text(`ID: Null`);
	$TARGET.attr("data-userpkmn-id", "")

	$(this).find(".btn-danger").remove()

	await axios.post(`${BASE_URL}/card/edit/${USER_ID}/delete`, {
			slot_id : SLOT_ID
	})

	
})

$("#delete-user-form").on("submit", async function(evt) {
    evt.preventDefault();
	console.log("Clicked!")

    $(".alert").empty();

	// remove any previous error message styling
	if ($(".alert").hasClass("alert-danger")) {
		$(".alert").toggleClass("alert-danger");
	}
	if ($(".alert").hasClass("alert-success")) {
		$(".alert").toggleClass("alert-success");
	}
    
    const USER_ID = $(this).attr("data-user-id");

    const RESP = await axios.post(`/profile/${USER_ID}/delete`);
    
    if (RESP.data == "FALSE") {
        $(".alert")
				.css("display", "block")
				.toggleClass("alert-danger")
				.append(`<p>Invalid Action.</p>`);
    }
    else if (RESP.data == "TRUE") {
        window.location.replace(BASE_URL);
		// Not sure how to get the below alert working ,,
		// $(".alert")
		// 		.css("display", "block")
		// 		.toggleClass("alert-success")
		// 		.append(`<p>Account was successfully deleted!</p>`);
    }
})