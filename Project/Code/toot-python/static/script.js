
(function () {

  $('#live-chat header').on('click', function () {

    $('.chat').slideToggle(300, 'swing');
    $('.chat-message-counter').fadeToggle(300, 'swing');

  });

  $('.chat-close').on('click', function (e) {

    e.preventDefault();
    $('#live-chat').fadeOut(300);

  });

})();

function addMsg() {
  let currentDate = new Date();
  let time = currentDate.getHours() + ":" + currentDate.getMinutes();
  console.log(time);
  var textMsg;
  textMsg = document.getElementById("input1").value;
  if (textMsg != "") {
    y = document.getElementById("chatStart");
    y.insertAdjacentHTML('beforeend', '<div class="chat-message clearfix"><img src="http://gravatar.com/avatar/2c0ad52fc5943b78d6abe069cc08f320?s=32" alt="" width="32" height="32"><div class="chat-message-content clearfix"><span class="chat-time">' + time + '</span><h5>Marc Biedermann</h5><p>' + textMsg + '</p></div></div>');
    document.getElementById("input1").value = "";
  }
}