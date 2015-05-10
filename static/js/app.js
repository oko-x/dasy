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

function handleData(data){
	var target = $("<div class='alert-box success decisionEval'>"+data+"</div>");
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

$(document).ready(function(){
	$(".collapsedContent").each(function(){
		$(this).css("height", "auto");
		$(this).css("height", $(this).height());
		$(this).addClass("collapsed");
	});
	console.log($(".itemWrapper:first-of-type"));
	$(".itemWrapper:first-of-type .fa-plus").click();
});