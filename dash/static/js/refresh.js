$(document).ready(function(){
	$("#newsBut").click(function(){
		// alert("CLICKED REFRESH");
		$("#newsBut").addClass("faa-spin animated");
		$.ajax({
			data : {
				name:"news"
			},
			type : "POST",
			url : "/update"
		}).done(function(data){
			$("#newsBut").removeClass("faa-spin animated");
			if(data.data){
				// alert(data.data);
				$("#newsfeed").prepend(data.data);
			}
		})
	})
})

$(document).ready(function(){
	$("#loadMore").click(function(){
		alert("CLICKED REFRESH");
		$("#loadMore").hide();
		$("#lm").append("<i id='tmp' class='fas fa-spinner faa-spin animated'></i>");
		$.ajax({
			data : {
				name:"news"
			},
			type : "POST",
			url : "/loadMore"
		}).done(function(data){
			$("#tmp").remove();
			if(data.data){
				// alert(data.data);
				$("#newsfeed").append(data.data);
			}
			$("#loadMore").show();
		})
	})
})