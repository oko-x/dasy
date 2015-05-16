$(document).foundation();

function openContent(elem){
	var target = $(elem).siblings(".collapsedContent");
	if(target.hasClass("collapsed")){
		$(elem).parent().parent().find(".fa-minus").removeClass("fa-minus").addClass("fa-plus");
		$(elem).parent().parent().find(".collapsedContent").addClass("collapsed");
		target.removeClass("collapsed");
		$(elem).removeClass("fa-plus").addClass("fa-minus");
	}else{
		target.addClass("collapsed");
		$(elem).removeClass("fa-minus").addClass("fa-plus");
	}
}

function handleInviteAccept(data, inviteId, decisionId){
	handleData(data);
	$.get( window.location.href + "decision/" + decisionId + "/info/" + inviteId, function( data ) {
		$("#decisions .empty_note").remove();
		$("#decisions").append(data);
		$("#decisions .spinnerWrapper").fadeOut(300);
	});
}

function handleInviteResult(data){
	handleData(data);
	var accepted = false;
	if(data = "Invite sent and accepted"){
		accepted = true;
	}
	$.get( window.location.href + "simple", function( data ) {
		var data = $(data);
		$("#invited").html(data.find("#invited").html());
		$("#uninvited").html(data.find("#uninvited").html());
		$("#invited, #uninvited").find(".spinnerWrapper").fadeOut(300);
		if(accepted){
			$("#pairwiseButton").show().trigger("mouseenter");
		}
	});
}

function handleData(data){
	var target = $("<div class='alert-box success custom'>"+data+"</div>");
	var button = $("<a href='#' class='close'>&times;</a>").click(function(){
		$(this).parent().slideUp(300, function(){
			$(this).remove();
		});
	});
	target.append(button).prependTo("body");
	target.slideUp(0, function(){
		$(this).slideDown(300);
	});
	setTimeout(function(){
		target.slideUp(300, function(){
			$(this).remove();
		});
	}, 3000);
}

function initCollapsed(){
	$(".collapsedContent").each(function(){
		$(this).css("height", "auto");
		$(this).css("height", $(this).height());
		$(this).addClass("collapsed");
	});
	$(".itemWrapper:first-of-type .fa-plus").click();
}

$(document).ready(function(){
	initCollapsed();
});