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

		let response = await axios.post(`http://localhost:5000/catch/${gennedId}`, {
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
