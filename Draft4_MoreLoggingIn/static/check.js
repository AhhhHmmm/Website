$(document).ready(function() {

	$('form').each(function() {
		$(this).on('submit', function(event) {

			var this_form = $(this);

			$.ajax({
				// Send the part.id, user.id, and user response.
				data : 
				{ 
					answer : $(this).find("input[name='answer']").val(),
					part_id : $(this).find("input[name='part_id']").val(),
					user_id : $(this).find("input[name='user_id']").val()
				},
				type : 'POST',
				url : '/check'
			})
			.done(function(data) {

				// Using the passed back message of whether correct or edit the html to display this.
				var message = 'Correct? : ' + data.correct;
				if (data.correct)
				{
					this_form.find(".answer_reaction").removeClass("glyphicon-remove").addClass("glyphicon glyphicon-ok");
				}
				else
				{
					this_form.find(".answer_reaction").removeClass("glyphicon-ok").addClass("glyphicon glyphicon-remove");
				}
				console.log(message);
			});

			event.preventDefault();

		});
	});

});