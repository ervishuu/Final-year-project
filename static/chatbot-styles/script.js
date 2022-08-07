jQuery(document).ready(function($) {
	jQuery(document).on('click', '.iconInner', function(e) {
		jQuery(this).parents('.botIcon').addClass('showBotSubject');
		$("[name='msg']").focus();
	});

	jQuery(document).on('click', '.closeBtn, .chat_close_icon', function(e) {
		jQuery(this).parents('.botIcon').removeClass('showBotSubject');
		jQuery(this).parents('.botIcon').removeClass('showMessenger');
	});

	jQuery(document).on('submit', '#botSubject', function(e) {
		e.preventDefault();

		jQuery(this).parents('.botIcon').removeClass('showBotSubject');
		jQuery(this).parents('.botIcon').addClass('showMessenger');
	});

	/* Chatboat Code */
	$(document).on("submit", "#messenger", function(e) {

		e.preventDefault();

		var val = $("[name=msg]").val().toLowerCase();
		var mainval = $("[name=msg]").val();
botResponse(mainval);
		function botResponse(rawText) {

              // Bot Response
              $.get("/get", { msg: mainval }).done(function (data) {
                console.log(mainval);
                console.log(data);
                const msgText = data;
                appendMsg(msgText);
              });

            }
            $('.Input_field').val("");



		name = '';
		nowtime = new Date();
		nowhoue = nowtime.getHours();

		function userMsg(msg) {
			$('.Messages_list').append('<div class="msg user"><span class="avtr"><figure style="background-image: url(https://miro.medium.com/max/1050/1*lyyXmbeoK5JiIBNCnzzjjg.png)"></figure></span><span class="responsText">' + mainval + '</span></div>');
		};
		function appendMsg(msg) {
			$('.Messages_list').append('<div class="msg"><span class="avtr"><figure style="background-image: url(https://img.freepik.com/free-vector/robot-vector-chat-bot-concept-illustration-virtual-assistant-banner-talk-bubble-speech-digital_111651-653.jpg?w=740)"></figure></span><span class="responsText">' + msg + '</span></div>');
			$("[name='msg']").val("");
		};


		userMsg(mainval);


		var lastMsg = $('.Messages_list').find('.msg').last().offset().top;
		$('.Messages').animate({scrollTop: lastMsg}, 'slow');
	});
	/* Chatboat Code */
})