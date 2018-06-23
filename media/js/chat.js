var last_chat_id=0;
var interval_sojusz;
var chat_get_url;
function init_sojusz_chat(url){
    chat_get_url=url;
	if(interval_sojusz){
		clearInterval(interval_sojusz);
	}
	chat_sojusz();
	interval_sojusz = setInterval(chat_sojusz,2500);
}

function chat_sojusz(){
	if(!$('#chat_sojusz'))return false;
	$.ajax({
   		type: "POST",
   		url: chat_get_url+"?id="+last_chat_id,
		dataType: "json",
		//async:false,
        success: function(data){
			$.each(data.rows, function(i, row){
				var div = $("<div/>").attr("class", "row");
				$("<span/>").attr("class",'chat_user').html(row.user+":").appendTo(div);
				$("<span/>").attr("class",'chat_wiadomosc').html(row.wiadomosc).appendTo(div);
				div.appendTo('#chat_sojusz');
				last_chat_id = row.id;
			})
		},
    });
}

function chat_sojusz_send(url){
	var wiadomosc = $('#id_chat_message').val();
	if(!wiadomosc.length>0)return false;
	$('#id_chat_message').val("");
	$.ajax({
   		type: "POST",
   		url: url,
		data: {"msg":wiadomosc},
		dataType: "text",
		//async:false,
        success: function(data){
			init_sojusz_chat(chat_get_url);
		},
    });
}
