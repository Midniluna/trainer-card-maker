const BASE_URL = 'http://localhost:5000'


// Used to submit user's attempt to catch a pokemon

$("#guess-pokemon-form").on("submit", async function (evt) {
	evt.preventDefault();

	// Clear the error message contents + hide the error message element
	$(".alert").empty();

	// remove any previous error message styling
	if ($(".alert").hasClass("alert-danger")) {
		$(".alert").toggleClass("alert-danger");
	} else if ($(".alert").hasClass("alert-success")) {
		$(".alert").toggleClass("alert-success");
	}

	let species = "";

	let $genned = $(".genned-mon").closest("div");
	let gennedId = $genned.attr("data-genned-id");

	if ($("#species").val() !== "") {
		species = $("#species").val().toLowerCase();

		let response = await axios.post(`${BASE_URL}/catch/${gennedId}`, {
			species,
		});
		// console.log(response.data);

		if (response.data === null) {
			return;
		} else if (response.data === "Failed") {
			$("#species").val() == "";

			// error message content is always cleared at the start, so always re-append error when catch-attempt is failed
			$(".alert")
				.css("display", "block")
				.toggleClass("alert-danger")
				.append(`<p>That is the incorrect pokemon. Check your spelling!</p>`);
		} else if (response.data === "Success") {
			$("#species").val() == "";
			// window.location.replace("http://localhost:5000/home");
			$(".genned-mon-content").empty();
			$(".alert")
				.toggleClass("alert-success")
				.css("display", "block")
				.append(`<p>Congrats! You've caught a(n) ${species}!</p>`);
			$(".redirect").append(`
            <br>
            <a href="/home" class="btn btn-lg">Return Home</a>`);
		}
	}

	return;
});



// --------------------------------------------------------


// This is to allow user to edit their card

$(".select-slot").on("click", async function (evt) {
	evt.preventDefault();
	let $target = $(this)

	let $active = $(".active");

	// If there are no selected buttons, let user select
	if ($active.length === 0) {
		$target.toggleClass("active");
	} 

	else if ($active.length === 1) {
		// if target is the "active" button, deselect
		if ($target.hasClass("active")) {
			$target.toggleClass("active");
		}
		// If user selects one slot and then another slot, swap the pokemons' positions
		else {
			let slot = $active.attr("data-slot-id")
			let slot2 = $target.attr("data-slot-id")
			let pkmn_id = $active.attr("data-userpkmn-id")
			console.log(pkmn_id)
			let pkmn2_id = $target.attr("data-userpkmn-id")
			console.log(pkmn2_id)
			let user_id = $(".card-container").attr("data-user-id")

			await axios.patch(`${BASE_URL}/card/edit/${user_id}/submit`, {
				slot,
				slot2,
				pkmn_id,
				pkmn2_id,
			})

			// Swap pokemon data on DOM

			let $img = $active.parent().find(".pokemon-image");
			let $nickname = $active.parent().find(".nickname");
			let $species = $active.parent().find(".species");
			let $id = $active.parent().find(".pkmnID");

			let $img2 = $target.parent().find(".pokemon-image");
			let $nickname2 = $target.parent().find(".nickname");
			let $species2 = $target.parent().find(".species");
			let $id2 = $target.parent().find(".pkmnID")

			// Save data from first slot to append to second slot and vice versa
			let swapimg = $img.attr("src")
			let swapnickname = $nickname.text()
			let swapspecies = $species.text()
			let swapid =  $id.text()

			let swapimg2 = $img2.attr("src")
			let swapnickname2 = $nickname2.text()
			let swapspecies2 = $species2.text()
			let swapid2 =  $id2.text()
			
			// Fill first slot's data with data from second slot
			$img.attr("src", swapimg2);
			$nickname.text(swapnickname2);
			$species.text(swapspecies2);
			$id.text(swapid2)

			// Now fill second slot's data with data from first slot
			$img2.attr("src", swapimg);
			$nickname2.text(swapnickname);
			$species2.text(swapspecies);
			$id2.text(swapid)

			$active.toggleClass("active");
		}
	}
	return
})



$(".select-mon").on("click", async function (evt) {
	evt.preventDefault();
	let $target = $(this)
	let $active = $(".active");

	if ($active.length === 0) {
		// if none selected, don't do anything
		console.log("None selected")
		return
	}
	else {
		
		let slot = $active.attr("data-slot-id")
		let pkmn_id = $target.attr("data-userpkmn-id")
		let user_id = $(".card-container").attr("data-user-id")
		
		
		// If pokemon ID is already in displayed card, ignore.
		let id_exists = $(`.edit-card`).find(`b:contains('ID: #${pkmn_id}')`)
		
			if (id_exists.length > 0 ) {
				return
			}
			
			// Otherwise, display new pokemon on screen.
			else {
				
				// Tell python slots are not being swapped
				let slot2 = "None" 
				let pkmn2_id = "None" 

				let resp = await axios.post(`${BASE_URL}/card/edit/${user_id}/submit`, {
					slot,
					slot2,
					pkmn_id,
					pkmn2_id,
				});
				img = $active.parent().find(".pokemon-image");
				nickname = $active.parent().find(".nickname");
				species = $active.parent().find(".species");
				id = $active.parent().find(".pkmnID");

				// Append delete button if adding a pokemon into a blank slot
				let $delete_btn = $(`<button class="btn btn-danger delete-slot" data-slot-id="${slot}">Remove</button>`)

				// If there's 
				if (species.text() == "No pokemon") {
					$delete_btn.insertAfter($active);
				}
	
				img.attr("src", resp.data.sprite);
				nickname.text(`${resp.data.nickname}`);
				species.text(`${resp.data.species}`);
				id.text(`ID: #${pkmn_id}`);

				$active.toggleClass("active")

			}
			

	}
	return
})

// class="btn btn-danger delete-slot" data-slot-id="{{slot}}"


$(".delete-slot").on("click", async function (evt) {
	evt.preventDefault();
	let $target = $(this).siblings(".select-slot")
	
	let slot_id = $target.attr("data-slot-id")
	let user_id = $(".card-container").attr("data-user-id")

	await axios.post(`${BASE_URL}/card/edit/${user_id}/delete`, {
			slot_id
	})

	
			
	// let resp = await axios.post(`${BASE_URL}/card/edit/${user_id}/delete`, {
	// 	slot,
	// 	pkmn_id,
	// });
	img = $target.parent().find(".pokemon-image");
	nickname = $target.parent().find(".nickname");
	species = $target.parent().find(".species");
	id = $target.parent().find(".pkmnID");

	img.attr("src", "http://localhost:5000/static/images/no-symbol.png");
	nickname.text("(nickname)");
	species.text("No pokemon");
	id.text(`ID: Null`);

	$(this).remove()
})
