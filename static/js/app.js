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

$(document).ready(function(){
	$(".collapsedContent").each(function(){
		$(this).css("height", "auto");
		$(this).css("height", $(this).height());
		$(this).addClass("collapsed");
	});
});