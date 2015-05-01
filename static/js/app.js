$(document).foundation();

function openContent(elem){
	$(elem).siblings(".collapsedContent").toggleClass("collapsed");
}

$(document).ready(function(){
	$(".collapsedContent").each(function(){
		$(this).css("height", "auto");
		$(this).css("height", $(this).height());
		$(this).addClass("collapsed");
	});
});