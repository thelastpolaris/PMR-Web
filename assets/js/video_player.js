function update_canvas() {
    var c1 = $("#videoCanvas");
    c1.css("left", "0px")

    var aspect_ratio = $("#videoPlayer")[0].videoWidth/$("#videoPlayer")[0].videoHeight
    var height = $("#videoPlayer").outerHeight()
    var width = height*aspect_ratio

    c1.css("width", width)
    c1.css("height", height)
    c1.css("left", ($("#videoPlayer").outerWidth() - width )/2)
    console.log("s", $("#videoPlayer").outerWidth())
}

$("#videoPlayer")[0].onloadedmetadata = function () {
    update_canvas()
}

window.onresize = function () {
    update_canvas()
}

var button = document.getElementById('toggle')

var json_data = null

function set_json_data(_json_data) {
    if (json_data == null) json_data = _json_data
}

setInterval(function () {
    video_player(json_data); // will get you a lot more updates.
}, 30);

function video_player(json_frames) {
    frame_data = null
    currentTime = $("#videoPlayer")[0].currentTime
    for( var i=0; i< json_frames.length; i++ ) {
        if (currentTime < json_frames[i]["second"]) {
            if(i == 0) return

            frame_data = json_frames[i]["data"]
            break
        }
    }
    if(frame_data == null) return

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
function closeFullscreen(document, elem) {
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

$(document).ready(function(){
	//INITIALIZE
	var video = $('#videoPlayer');
	update_canvas()

	//remove default control when JS loaded
	video[0].controls = false
    $('.control').show().css({'bottom': 0});
	$('.loading').fadeIn(500);
	$('.caption').fadeIn(500);

	//before everything get started
	video.on('loadedmetadata', function() {
		$('.caption').animate({'top':-45},300);

		//set video properties
		$('.current').text(timeFormat(0));
		$('.duration').text(timeFormat(video[0].duration));
		updateVolume(0, 0.7);

		//start to get video buffering data
		setTimeout(startBuffer, 150);

		//bind video events
		$('.videoContainer')
		.append('<div id="init"></div>')
		.hover(function() {
			$('.control').stop().animate({'bottom':0}, 500);
			$('.caption').stop().animate({'top':0}, 500);
		}, function() {
			if(!volumeDrag && !timeDrag){
				$('.control').stop().animate({'bottom':-45}, 500);
				$('.caption').stop().animate({'top':-45}, 500);
			}
		})
		.on('click', function() {
			$('#init').remove();
			$('.btnPlay').addClass('paused');
			$(this).unbind('click');
			video[0].play();
		});
		$('#init').fadeIn(200);
	});

	//display video buffering bar
	var startBuffer = function() {
		var currentBuffer = video[0].buffered.end(0);
		var maxduration = video[0].duration;
		var perc = 100 * currentBuffer / maxduration;
		$('.bufferBar').css('width',perc+'%');

		if(currentBuffer < maxduration) {
			setTimeout(startBuffer, 500);
		}
	};

	//display current video play time
	video.on('timeupdate', function() {
		var currentPos = video[0].currentTime;
		var maxduration = video[0].duration;
		var perc = 100 * currentPos / maxduration;
		$('.timeBar').css('width',perc+'%');
		$('.current').text(timeFormat(currentPos));
	});

	//CONTROLS EVENTS
	//video screen and play button clicked
	video.on('click', function() { playpause(); } );
	$('.btnPlay').on('click', function() { playpause(); } );
	var playpause = function() {
		if(video[0].paused || video[0].ended) {
			$('.btnPlay').addClass('paused');
			video[0].play();
		}
		else {
			$('.btnPlay').removeClass('paused');
			video[0].pause();
		}
	};

	//speed text clicked
	$('.btnx1').on('click', function() { fastfowrd(this, 1); });
	$('.btnx3').on('click', function() { fastfowrd(this, 3); });
	var fastfowrd = function(obj, spd) {
		$('.text').removeClass('selected');
		$(obj).addClass('selected');
		video[0].playbackRate = spd;
		video[0].play();
	};

	//stop button clicked
	$('.btnStop').on('click', function() {
		$('.btnPlay').removeClass('paused');
		updatebar($('.progress-player').offset().left);
		video[0].pause();
	});

	//fullscreen button clicked
	$('.btnFS').on('click', function() {
	    var isFullscreenNow = $(document)[0].webkitFullscreenElement !== null
		if(isFullscreenNow) {
		    closeFullscreen($(document)[0], $('.videoContainer')[0])
            $("#videoPlayer").css({"maxHeight": "400px"})
            $("#videoPlayer").css("width", "")
            $("#videoPlayer").css("height", "")
		} else {
		    openFullscreen($('.videoContainer')[0])
		    $("#videoPlayer").css({"maxHeight": "initial"})
		    $("#videoPlayer").css("width", "100%")
		    $("#videoPlayer").css("height", "100%")

		}

	});

	function onFullScreen(e) {
        var isFullscreenNow = document.fullscreenElement !== null
        if(isFullscreenNow == false) {
            $("#videoPlayer").css("width", "")
            $("#videoPlayer").css("height", "")
        }
        update_canvas()
    }

    $("#videoContainer")[0].addEventListener('fullscreenchange', onFullScreen)

	//light bulb button clicked
	$('.btnLight').click(function() {
		$(this).toggleClass('lighton');

		//if lightoff, create an overlay
		if(!$(this).hasClass('lighton')) {
			$('body').append('<div class="overlay"></div>');
			$('.overlay').css({
				'position':'absolute',
				'width':100+'%',
				'height':$(document).height(),
				'background':'#000',
				'opacity':0.9,
				'top':0,
				'left':0,
				'z-index':999
			});
			$('.videoContainer').css({
				'z-index':1000
			});
		}
		//if lighton, remove overlay
		else {
			$('.overlay').remove();
		}
	});

	//sound button clicked
	$('.sound').click(function() {
		video[0].muted = !video[0].muted;
		$(this).toggleClass('muted');
		if(video[0].muted) {
			$('.volumeBar').css('width',0);
		}
		else{
			$('.volumeBar').css('width', video[0].volume*100+'%');
		}
	});

	//VIDEO EVENTS
	//video canplay event
	video.on('canplay', function() {
		$('.loading').fadeOut(100);
	});

	//video canplaythrough event
	//solve Chrome cache issue
	var completeloaded = false;
	video.on('canplaythrough', function() {
		completeloaded = true;
	});

	//video ended event
	video.on('ended', function() {
		$('.btnPlay').removeClass('paused');
		video[0].pause();
	});

	//video seeking event
	video.on('seeking', function() {
		//if video fully loaded, ignore loading screen
		if(!completeloaded) {
			$('.loading').fadeIn(200);
		}
	});

	//video seeked event
	video.on('seeked', function() { });

	//video waiting for more data event
	video.on('waiting', function() {
		$('.loading').fadeIn(200);
	});

	//VIDEO PROGRESS BAR
	//when video timebar clicked
	var timeDrag = false;	/* check for drag event */
	$('.progress-player').on('mousedown', function(e) {
		timeDrag = true;
		updatebar(e.pageX);
	});
	$(document).on('mouseup', function(e) {
		if(timeDrag) {
			timeDrag = false;
			updatebar(e.pageX);
		}
	});
	$(document).on('mousemove', function(e) {
		if(timeDrag) {
			updatebar(e.pageX);
		}
	});
	var updatebar = function(x) {
		var progress = $('.progress-player');

		//calculate drag position
		//and update video currenttime
		//as well as progress bar
		var maxduration = video[0].duration;
		var position = x - progress.offset().left;
		var percentage = 100 * position / progress.width();
		if(percentage > 100) {
			percentage = 100;
		}
		if(percentage < 0) {
			percentage = 0;
		}
		$('.timeBar').css('width',percentage+'%');
		video[0].currentTime = maxduration * percentage / 100;
	};

	//VOLUME BAR
	//volume bar event
	var volumeDrag = false;
	$('.volume').on('mousedown', function(e) {
		volumeDrag = true;
		video[0].muted = false;
		$('.sound').removeClass('muted');
		updateVolume(e.pageX);
	});
	$(document).on('mouseup', function(e) {
		if(volumeDrag) {
			volumeDrag = false;
			updateVolume(e.pageX);
		}
	});
	$(document).on('mousemove', function(e) {
		if(volumeDrag) {
			updateVolume(e.pageX);
		}
	});
	var updateVolume = function(x, vol) {
		var volume = $('.volume');
		var percentage;
		//if only volume have specificed
		//then direct update volume
		if(vol) {
			percentage = vol * 100;
		}
		else {
			var position = x - volume.offset().left;
			percentage = 100 * position / volume.width();
		}

		if(percentage > 100) {
			percentage = 100;
		}
		if(percentage < 0) {
			percentage = 0;
		}

		//update volume bar and video volume
		$('.volumeBar').css('width',percentage+'%');
		video[0].volume = percentage / 100;

		//change sound icon based on volume
		if(video[0].volume == 0){
			$('.sound').removeClass('sound2').addClass('muted');
		}
		else if(video[0].volume > 0.5){
			$('.sound').removeClass('muted').addClass('sound2');
		}
		else{
			$('.sound').removeClass('muted').removeClass('sound2');
		}
	};

	//Time format converter - 00:00
	var timeFormat = function(seconds){
		var m = Math.floor(seconds/60)<10 ? "0"+Math.floor(seconds/60) : Math.floor(seconds/60);
		var s = Math.floor(seconds-(m*60))<10 ? "0"+Math.floor(seconds-(m*60)) : Math.floor(seconds-(m*60));
		return m+":"+s;
	};
});