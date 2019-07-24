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
    uploadFile()

    e.disabled = true

}

function _(el) {
  return document.getElementById(el);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function uploadFile() {
  var file = _("uploadVideoFile").files[0];
  // alert(file.name+" | "+file.size+" | "+file.type);
  var formdata = new FormData();
  formdata.append("file1", file);
  formdata.append("_xsrf", getCookie("_xsrf"))
  var ajax = new XMLHttpRequest();
  ajax.upload.addEventListener("progress", progressHandler, false);
  ajax.addEventListener("load", completeHandler, false);
  ajax.addEventListener("error", errorHandler, false);
  ajax.addEventListener("abort", abortHandler, false);
  ajax.open("POST", "/addtask");
  ajax.send(formdata);
}

function progressHandler(event) {
  _("videoUploadProgressLabel").children[0].innerHTML = "Uploading File";
  var percent = Math.round((event.loaded / event.total) * 100);
  _("videoUploadProgressPercentage").children[0].innerHTML = percent + "%";
  _("videoUploadProgressBar").style.width = percent + "%";

//  _("status").innerHTML = Math.round(percent) + "% uploaded... please wait";
}

function completeHandler(event) {
  _("videoUploadProgressLabel").children[0].innerHTML = event.target.responseText;
}

function errorHandler(event) {
  _("videoUploadProgressLabel").children[0].innerHTML = "Upload Failed";
}

function abortHandler(event) {
  _("videoUploadProgressLabel").children[0].innerHTML = "Upload Aborted";
}

function uploadImages(e) {
    document.getElementById("videos-tab").disabled = true
    document.getElementById("youtube-tab").disabled = true

    e.disabled = true
}

function uploadYouTube() {
    document.getElementById("images-tab").disabled = true
    document.getElementById("videos-tab").disabled = true
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
    document.getElementById("uploadVideoFile").blur()

    document.getElementById("video-upload-progress").style.opacity = 0

    document.getElementById("submit-task").disabled = true;
}