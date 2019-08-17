function update_canvas() {
    var c1 = $("#videoCanvas");
    c1.css("left", "0px")
    c1.css("width", $("#videoPlayer").outerWidth())
    c1.css("height", $("#videoPlayer").outerHeight())
    c1.css("left", ($("#videoPlayer").outerWidth(true) - $("#videoPlayer").outerWidth())/2 )
}

$("#videoPlayer")[0].onloadedmetadata = function () {
    update_canvas()
}

window.onresize = function () {
    update_canvas()
}

var button = document.getElementById('toggle')

function video_player(json_frames) {
    console.log($("#videoPlayer").offset().left)

    currentTime = $("#videoPlayer")[0].currentTime
    frame_data = json_frames[Math.floor(currentTime)]["data"]

    var c1 = document.getElementById("videoCanvas");
    var c1_context = c1.getContext("2d");
    c1_context.fillStyle = "#f00";
    c1_context.clearRect(0, 0, c1.width, c1.height);
    c1_context.strokeStyle = "red";
    var width = $("#videoPlayer")[0].width
    var height = $("#videoPlayer")[0].height
    var woffset = c1.width - $("#videoPlayer")[0].videoWidth

    for( var i=0; i< frame_data.length; i++ ) {
        var box = frame_data[i]["bounding_box"]
        var bottom = box["bottom"]*c1.height
        var top = box["top"]*c1.height
        var left = box["left"]*c1.width
        var right = box["right"]*c1.width

        c1_context.strokeRect(left, top, right - left, bottom - top);
    }
}


window.onload = function() {
  // Video
  var video = document.getElementById("videoPlayer");
  video.controls = false;

  // Buttons
  var playButton = document.getElementById("play-pause");
  var muteButton = document.getElementById("mute");
  var fullScreenButton = document.getElementById("full-screen");

  // Sliders
  var seekBar = document.getElementById("seek-bar");
  var volumeBar = document.getElementById("volume-bar");

  playButton.addEventListener("click", function() {
  if (video.paused == true) {
    // Play the video
    video.play();

    // Update the button text to 'Pause'
    playButton.innerHTML = "Pause";
  } else {
    // Pause the video
    video.pause();

    // Update the button text to 'Play'
    playButton.innerHTML = "Play";
  }
});

    // Event listener for the mute button
    muteButton.addEventListener("click", function() {
      if (video.muted == false) {
        // Mute the video
        video.muted = true;

        // Update the button text
        muteButton.innerHTML = "Unmute";
      } else {
        // Unmute the video
        video.muted = false;

        // Update the button text
        muteButton.innerHTML = "Mute";
      }
    });

    // Event listener for the full-screen button
fullScreenButton.addEventListener("click", function() {
    var video_container = document.getElementById("videoContainer");
  var isFullscreenNow = document.webkitFullscreenElement !== null
    if(  document.fullscreenElement || /* Standard syntax */
      document.webkitFullscreenElement || /* Chrome, Safari and Opera syntax */
      document.mozFullScreenElement ||/* Firefox syntax */
      document.msFullscreenElement) {
          closeFullscreen(video_container)

          $("#videoPlayer").css("width", "initial")
          $("#videoPlayer").css("height", "initial")
        fullScreenButton.innerHTML = "FullScreen"

    } else {
        openFullscreen(video_container)
          $("#videoPlayer").css("width", "100%")
          $("#videoPlayer").css("height", "100%")
        fullScreenButton.innerHTML = "Close"
    }
});

    // Event listener for the seek bar
    seekBar.addEventListener("change", function() {
      // Calculate the new time
      var time = video.duration * (seekBar.value / 100);

      // Update the video time
      video.currentTime = time;
    });

    // Update the seek bar as the video plays
    video.addEventListener("timeupdate", function() {
      // Calculate the slider value
      var value = (100 / video.duration) * video.currentTime;

      // Update the slider value
      seekBar.value = value;
    });

    // Event listener for the volume bar
    volumeBar.addEventListener("input", function() {
      // Update the video volume
      video.volume = volumeBar.value;
    });

    $('.progress').slider({
        value: 0,
        orientation: "horizontal",
        range: "min",
        animate: true
    });
}

function onFullScreen(e) {
  var isFullscreenNow = document.fullscreenElement !== null
  if(isFullscreenNow == false) {
    $("#videoPlayer").css("width", "initial")
          $("#videoPlayer").css("height", "initial")
  }
  update_canvas()
}

document.getElementById("videoContainer").addEventListener('fullscreenchange', onFullScreen)

/* View in fullscreen */
function openFullscreen(elem) {
  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if (elem.mozRequestFullScreen) { /* Firefox */
    elem.mozRequestFullScreen();
  } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari and Opera */
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) { /* IE/Edge */
    elem.msRequestFullscreen();
  }
}

/* Close fullscreen */
function closeFullscreen(elem) {
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if (document.mozCancelFullScreen) { /* Firefox */
    document.mozCancelFullScreen();
  } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
    document.webkitExitFullscreen();
  } else if (document.msExitFullscreen) { /* IE/Edge */
    document.msExitFullscreen();
  }
}