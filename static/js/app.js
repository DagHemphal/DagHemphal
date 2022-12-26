$(document).ready(function(e) {
	var scrollp;
	var scrollm;
	var move = false;
	var og;

	//var drake = dragula([document.querySelector('#order')]);
	$("#order").on('taphold', function (e) {
		e.preventDefault();
		move = true;
		e.originalEvent = og;
		$(e.target).trigger('touchstart');
	
	});

	$("#order").on('touchstart', function (e) {
		if (e.originalEvent) {
			og = e.originalEvent;
		}
		if (move) {
			e.preventDefault();
			var yPos = og.touches[0].clientY;
			var target = e.target;
			if (target.localName != "li")
				target = target.parentNode;
			
			$(target).clone().addClass("gu-mirror").appendTo("body");
			$(target).addClass("gu-transit");
			$(".gu-mirror").css("top", yPos - 40);
		}	
		//lägg till markering för hålla knapp
	});

	$("#order").on('touchmove', function (e) {
		if (move) {
			e.preventDefault();
			target = e.target;
			var ogpos = target.offsetTop;
			var yPos = e.originalEvent.touches[0].pageY;
			var ycPos = e.originalEvent.touches[0].clientY;
			var winHeight = window.innerHeight;

			$(".gu-mirror").css("top", ycPos - 40);


			if (ycPos >= winHeight * 0.85) {
				var maxdistance = (winHeight * 0.15);
				var distance = value_limit((ycPos) - (winHeight * 0.85), 0, maxdistance);
				clearInterval(scrollp);
				clearInterval(scrollm);
				var speed = (8 * (1 - (distance/maxdistance) ) + 2);
				scrollp = setInterval(scrollplus, speed);
			}
			else if (ycPos <= winHeight * 0.15) {
				var maxdistance = (winHeight * 0.15);
				var distance = value_limit(ycPos, 0, maxdistance);
				clearInterval(scrollp);
				clearInterval(scrollm);
				var speed = (8 * ((distance/maxdistance) ) + 2);
				scrollm = setInterval(scrollminus, speed);
			}
			else {
				clearInterval(scrollp);
				clearInterval(scrollm);
			}

			var numchild = $("#order")[0].childElementCount;
			yPos = value_limit(yPos, 41, 82*numchild+41); //fixa 1060
			var child = Math.floor(yPos/82);
			var list = $("#order")[0].children[child]; //0 - childElementCount 12

			if (target.localName != "li")
				target = target.parentNode;
			if (yPos >= 82*numchild+41) //fixa 1060
				$(target).appendTo("#order");
			else
				$(target).insertBefore(list);
		}

	});

	$("#order").on('touchend', function (e) {
		if (move) {
			e.preventDefault();
			clearInterval(scrollp);
			clearInterval(scrollm);
			$(".gu-mirror").remove();
			$("#order>li").removeClass("gu-transit");
			move = false;
		}
		
	});

	history.replaceState({page: 1}, "home page");
	window.addEventListener('popstate', (event) => {
		console.log(`location: ${document.location}, state: ${JSON.stringify(event.state)}`);
		if (event.state.page == 1) {
			$("#wrapper").hide();
			$("form").show();
		} else if (event.state.page == 2) {
			$("#wrapper").show();
			$("form").hide();
		}
	});

	$.get( "./api/get_games/", function( data ) {
		console.log(data);
		var select = $("#game");
		var ret;
		for (const [game_id, date] of data) {
			ret += "<option value="+game_id+">"+date+" spel:"+game_id+"</option>"
		};
		
		select.append(ret);
	});

	$.get( "./api/get_users/", function( data ) {
		console.log(data);
		var usernameInput = document.getElementById("usernameInput");		
		usernameInput.addEventListener("keyup", function () {autoComplete(data);}, false);
	});

	$("form").submit(function (e){
		e.preventDefault();
		//var username = localStorage.getItem('username')
		//if(username === null)
		var game_id = $("#game").val();
		console.log(game_id);
		var username = $("input[name ='username']").val();
		$("#best").empty()
		$("#best").append("Bäst&nbsp;&nbsp;  -  &nbsp;" + username);
		var data = [];
		data.push({
	  			game_id: game_id,
	  			username: username
	  		});

		$.ajax({
		    type: 'POST',
		    url: './api/join/',
		    data: JSON.stringify(data),
		    success: function( data ) {
			  console.log(data);
			  var html = "";
			  if (typeof data[0][1] === 'string') {
				$('#points').remove();
				$('#top').append('<a id="points" href="./info/">Se poängtavla</a>');
			  }
			  for (li of data) {
			  	if (typeof li[1] === 'string') {
			  		html += '<li class="must">'
					html +=	'<div class="id">'+ li[0] +'</div>'
					html += "<div class='name'>"+ li[1] +"</div>";
					html += '</li>'
					$('#send').off('click');
					$('#order').off('taphold');
			  	}
			  	else {
				  	html += '<li class="must">'
					html +=	'<div class="id" value="'+li[0]+'">'+ li[1] +'</div>'
					html += '</li>'
				}
			  }
			  $("#order").empty();
			  $("#order").append(html);
			  $("#wrapper").show();
			  $("form").hide();
			  localStorage.setItem('game_id', game_id);
			  if (data)
			  localStorage.setItem('username', username);

			  history.pushState({ page: 2 }, "user page");
			},
			contentType: "application/json",
			dataType: 'json'
		});
  	});

  	/*if(localStorage.getItem('username') !== null) {
		$("form").trigger('submit');
	}*/

  	$("#send").click(function (e){
  		if (confirm("Är du säker på dina alternativ?")){
	  		var data = [];
	  		var username = localStorage.getItem('username');
	  		data.push({
	  			username: username
	  		});
			$('.id').each(function(index){
			    data.push({
			        round_number: $(this).text(),
			        placement: index + 1
			    });
			});
			console.log(data);
	  		$.ajax({
			    type: 'POST',
			    url: './api/done/',
			    data: JSON.stringify (data),
			    success: function(data) { 
			    	console.log(data);
			    	if (data['message'])
			    		alert(data['message']);
			    	else {
				    	for (const [i, li] of data.entries()) {
				    		html = "<div class='name'>"+ li +"</div>";
				    		$(".must").eq(i).append(html);
				    		$('#send').off('click');
				    		$('#order').off('taphold');
				    	}
				    	$('#top').append('<a id="points" href="./info/">Se poängtavla</a>');

					}			    	
			    },
			    contentType: "application/json",
			    dataType: 'json'
			});
	  	}
  	})

});


function value_limit(val, min, max) {
  return val < min ? min : (val > max ? max : val);
}

function scrollplus(){
	var scrollPos = $(window).scrollTop();
	$(document).scrollTop(scrollPos + 3);
}
function scrollminus(){
	var scrollPos = $(window).scrollTop();
	$(document).scrollTop(scrollPos - 3);
}


function autoComplete(usersData) {
	//loop through above array
	//Initially remove all elements ( so if user erases a letter or adds new letter then clean previous outputs)
	var game_id = $("#game").val();
	let userDataGame = usersData[game_id-1];
	var usernameInput = document.getElementById("usernameInput");
	
	removeElements();
	for (let i of userDataGame) {
		//convert input to lowercase and compare with each string
		if (i.toLowerCase().startsWith(usernameInput.value.toLowerCase()) && usernameInput.value != "") {
			//create li element
			let listItem = document.createElement("li");
			//One common class name
			listItem.classList.add("list-items");
			listItem.style.cursor = "pointer";
			listItem.setAttribute("onclick", "displayNames('" + i + "')");
			//Display matched part in bold
			let word = "<b>" + i.substr(0, usernameInput.value.length) + "</b>";
			word += i.substr(usernameInput.value.length);
			//display the value in array
			listItem.innerHTML = word;
			document.querySelector(".list").appendChild(listItem);
		}
	}
	usernameInput.scrollIntoView({behavior: "auto", block: "center", inline: "center"});
}

function displayNames(value) {
	var usernameInput = document.getElementById("usernameInput");
	usernameInput.value = value;
	removeElements();
}
function removeElements() {
	//clear all the item
	let items = document.querySelectorAll(".list-items");
	items.forEach((item) => {
	  item.remove();
	});
}
