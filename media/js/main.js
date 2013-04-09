$(function () {
	console.log(":Asd")
	$('.affix').affix()
})

function toInt(str){
	if(isNaN(parseInt(str))){
		return 0;
	} else {
		return parseInt(str);
	}
}


function tooltip(v,e,t) {
//do generowania chmurki
	if (!v.title||!document.createElement) return

		t=document.createElement("div")

			t.move=function(e) {

				e=e||event

					t.style.left=e.clientX+10+(document.documentElement.scrollLeft||document.body.scrollLeft)+"px"

					t.style.top=e.clientY-30+(document.documentElement.scrollTop||document.body.scrollTop)+"px"

			}

	t.hide=function(x) {

		v.title=t.innerHTML

			if (x=document.getElementById("tooltip")) document.body.removeChild(x)

	}

	t.move(e);

	t.id="tooltip"

		t.innerHTML=v.title;v.title=""

		document.body.appendChild(t)

		v.onmouseout=t.hide

		v.onmousemove=t.move

}

function czas_serwera(){
	v=new Date();
	var bxx=document.getElementById('czas_serwera');
	n=new Date();
	ss=czas;
	s=ss+Math.round((n.getTime()-v.getTime())/1000.);
	m=0;h=0;
	if(s>=0){
		if(s>59){
			m=Math.floor(s/60);
			s=s-m*60
		}
		if(m>59){
			h=Math.floor(m/60);
			m=m-h*60
		}
		if(s<10){
			s="0"+s
		}
		if(m<10){
			m="0"+m
		}
		bxx.innerHTML=h+":"+m+":"+s
	}
	czas=czas+1;
	window.setTimeout("czas_serwera();",999);

}


function set_max(obj_id,ile_mamy,ile_max){
	var obj_jquery = '#'+obj_id;
	if(ile_mamy>ile_max){
		if(ile_max==$(obj_jquery).val()){
			$(obj_jquery).val(0);
		} else {
			$(obj_jquery).val(ile_max);
		}
	} else {
		if(ile_mamy==$(obj_jquery).val()){
			$(obj_jquery).val(0);
		} else {
			$(obj_jquery).val(ile_mamy);
		}
	}
	$(obj_jquery).focus()
}


function set_ilosc(obj_id,max){
	var obj_jquery = '#'+obj_id;
	old_val = $(obj_jquery).val()
	if(old_val!=max){
		$(obj_jquery).val(max);
	} else {
		$(obj_jquery).val(0);
	}
	$(obj_jquery).focus();
}


function t(){
	v=new Date();
	var bxx=document.getElementById('bxx');
	n=new Date();
	ss=pp;
	s=ss-Math.round((n.getTime()-v.getTime())/1000.);
	m=0;h=0;
	if(s<0 && przeskok==0){
		przeskok = 1;
		document.location.href=site;
	} else if (s<0){
		przeskok = 1;
	}else{
		if(s>59){
			m=Math.floor(s/60);
			s=s-m*60
		}
		if(m>59){
			h=Math.floor(m/60);
			m=m-h*60
		}
		if(s<10){
			s="0"+s
		}
		if(m<10){
			m="0"+m
		}
		bxx.innerHTML=h+":"+m+":"+s
	}
	pp=pp-1;
	window.setTimeout("t();",999);

}

function edytuj_uprawnienia(id_usera){
	$.ajax({
			type: 'GET',
			url: '/game/sojusz/uprawnienia/'+id_usera+'/',
			timeout: 2000,
			cache: false,
			success: function(data){
				$("#uprawnienia_"+id_usera).html(data).show();
			},
			error: function(XMLHttpRequest, textStatus, errorThrown){
				alert("Problem z serwerem")
			}
		});
}


function zapisz_uprawnienia(form){
	$.ajax({
			type: 'GET',
			url: '/game/sojusz/uprawnienia/'+id_usera+'/',
			timeout: 2000,
			cache: false,
			success: function(data){
				$("#uprawnienia_"+id_usera).html(data).show();
			},
			error: function(XMLHttpRequest, textStatus, errorThrown){
				alert("Problem z serwerem")
			}
		});
}
