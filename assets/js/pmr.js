'use strict';

var GenerateToken = (function() {
	
	var $gen_token = $('#generate-token');

	$("#generate-token").click(function(){
    	$.post("/user",
    	{
            generate_token: true,
        },
        function(data, status){
    		$("#display-token").html(data)
  		});
	});
})();

var inputs = document.querySelectorAll( '.custom-file-input' );
Array.prototype.forEach.call( inputs, function( input )
{
	var label	 = input.nextElementSibling,
		labelVal = label.innerHTML;

	input.addEventListener( 'change', function( e )
	{
		var fileName = '';
		if( this.files && this.files.length > 1 )
			fileName = ( this.getAttribute( 'data-multiple-caption' ) || '' ).replace( '{count}', this.files.length );
		else
			fileName = e.target.value.split( '\\' ).pop();

		if( fileName )
			label.innerHTML = fileName;
		else
			label.innerHTML = labelVal;
	});
});

function uploadVideo(e) {
    document.getElementById("images-tab").disabled = true
    document.getElementById("youtube-tab").disabled = true

    document.getElementById("video-upload-progress").style.opacity = 1
    uploadFile("uploadVideoFile", _("videoUploadProgressLabel"),
    _("videoUploadProgressPercentage"), _("videoUploadProgressBar"), 0)

    e.disabled = true
}

function uploadImages(e) {
    document.getElementById("videos-tab").disabled = true
    document.getElementById("youtube-tab").disabled = true

    document.getElementById("image-upload-progress").style.opacity = 1
    uploadFile("uploadImages", _("imageUploadProgressLabel"),
    _("imageUploadProgressPercentage"), _("imageUploadProgressBar"), 1)

    e.disabled = true
}

function uploadYouTube(e) {
    var youtubeRegex = new RegExp('^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+');
    var yt_URL = $("#uploadYouTube").val()

    if(youtubeRegex.test(yt_URL) === true)
        _("images-tab").disabled = true
        _("videos-tab").disabled = true

        $("#yt-upload-progress").css('opacity', 1)

        uploadYTVideo(yt_URL)

    e.disabled = true
}

function _(el) {
  return document.getElementById(el);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function uploadFile(form_id, label, percent, bar, type) {
  var file = _(form_id).files[0];
  var formdata = new FormData();
  formdata.append("file1", file);
  formdata.append("_xsrf", getCookie("_xsrf"))
  formdata.append("type", type)
  var ajax = new XMLHttpRequest();
  ajax.upload.addEventListener("progress", function(e) { progressHandler(e, label, percent, bar) }, false);
  ajax.addEventListener("load", function(e) { completeHandler(e, label) }, false);
  ajax.addEventListener("error", function(e) { errorHandler(e, label) }, false);
  ajax.addEventListener("abort", function(e) { abortHandler(e, label) }, false);
  ajax.open("POST", "/uploadfile");
  ajax.send(formdata);
}

function uploadYTVideo(yt_URL) {
    var ws = new WebSocket("ws://localhost:8888/uploadyt");
    ws.onopen = function() {
       ws.send(yt_URL);
    };
    ws.onmessage = function (evt) {
        $("#ytUploadProgressLabel > span").html("Dowloading Video");
        var response = JSON.parse(evt.data)

        if (response["progress"]) {
            var percent = response["progress"];
            $("#ytUploadProgressPercentage > span").html(percent + "%");
            $("#ytUploadProgressBar").width(percent + "%");
        } else if(response["fileID"]) {
            _("fileID").value = response["fileID"]
        }
    };

    ws.onclose = function() {
        $("#ytUploadProgressLabel > span").html("Download Finished");
        _("submit-task").disabled = false
    }
}

function submitTask() {
  var formdata = new FormData();

  formdata.append("fileID", _("fileID").value)
  formdata.append("_xsrf", getCookie("_xsrf"))
  var ajax = new XMLHttpRequest();
      ajax.onreadystatechange = function(data) {
        if (this.readyState == 4 && this.status == 200) {
            $.notify({
                    icon: 'ni ni-check-bold',
                    message: "<b>Success!</b> New Task is added to the queue"
                },
                {
                    type: "success",
                    allow_dismiss: true,
                    placement: {
                        align: "center"
                    },
                });

            $('#add-task-modal').modal('hide');

            var task = JSON.parse(data["currentTarget"]["response"])
            console.log(task["image_url"])
            addTaskToList(task["image_url"], task["filename"], task["status"], task["current_stage"], task["completion"])

           }
        };
    ajax.open("POST", "/addtask", true);
    ajax.send(formdata);
}

function progressHandler(event, label, percentBar, bar) {
  label.children[0].innerHTML = "Uploading File";
  var percent = Math.round((event.loaded / event.total) * 100);
  percentBar.children[0].innerHTML = percent + "%";
  bar.style.width = percent + "%";
}

function completeHandler(event, label) {
    var status = ""
    if (event.target.status == 200) {
        _("submit-task").disabled = false
        status = "File Uploaded"
        _("fileID").value = event.target.responseText
    } else {
        status = "Not Uploaded"
    }
    label.children[0].innerHTML = status;
}

function errorHandler(event, label) {
  label.children[0].innerHTML = "Upload Failed";
}

function abortHandler(event, label) {
  label.children[0].innerHTML = "Upload Aborted";
}

function resetUploadForm() {
    var childDivs = document.getElementById("add-task-modal").getElementsByTagName('button');

    for( var i=0; i< childDivs.length; i++ )
    {
        childDivs[i].disabled = false;
    }

    var childDivs = document.getElementById("add-task-modal").getElementsByTagName('input');

    for( var i=0; i< childDivs.length; i++ )
    {
        var input_elem = childDivs[i]
        input_elem.value = '';

        var event = new Event('change');
        input_elem.dispatchEvent(event);
    }

    $("#uploadVideoFile").blur()
    $("#uploadImages").blur()
    $("#uploadYouTube").blur()

    $("#video-upload-progress").css('opacity', 0)
    $("#image-upload-progress").css('opacity', 0)
    $("#yt-upload-progress").css('opacity', 0)


    _("submit-task").disabled = true;
}