'use strict';

function taskRow(image_url, filename, status, current_stage, completion){
   return `<tr>
            <th scope="row">
              <div class="media align-items-center">
                <div class="avatar rounded-circle mr-3">
                  <img alt="Image placeholder" src=${image_url}>
                </div>
                <div class="media-body">
                  <span class="mb-0 text-sm">${filename}</span>
                </div>
              </div>
            </th>
            <td>
              <span class="badge badge-dot mr-4">
                ${status == 0 ? '<i class="bg-info"></i> Queued' : ''}
                ${status == 1 ? `<i class="bg-success"></i> Processing (${current_stage })` : ''}
                ${status == 2 ? '<i class="bg-success"></i> Finished' : ''}
                ${status == 3 ? '<i class="bg-warning"></i> Failed' : ''}
              </span>
            </td>
            <td>
              <div class="d-flex align-items-center">
                <span class="mr-2">${completion}%</span>
                <div>
                  <div class="progress">
                    <div class="progress-bar bg-success" role="progressbar" aria-valuenow="${completion}" aria-valuemin="0" aria-valuemax="100" style="width: ${completion}%;"></div>
                  </div>
                </div>
              </div>
            </td>
            <td class="text-right">
              <div class="dropdown">
                <a class="btn btn-sm btn-icon-only text-light" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  <i class="fas fa-ellipsis-v"></i>
                </a>
                <div class="dropdown-menu dropdown-menu-right dropdown-menu-arrow">
                  <a class="dropdown-item" href="#">Pause</a>
                  <a class="dropdown-item" href="#">Delete</a>
                </div>
              </div>
            </td>
            </tr>`;
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function addTaskToList(image_url, filename, status, current_stage, completion) {
    $("#taskLists").append(taskRow(image_url, filename, status, current_stage, completion))
}

function listTasks() {
    $('#taskTable').addClass('loading')

    var formdata = new FormData();
    formdata.append("_xsrf", getCookie("_xsrf"))

    $.ajax({
      url: '/',
      data: formdata,
      processData: false,
      contentType: false,
      type: 'POST',
      success: function(data){
        for (var d of data["tasks"]) {
            addTaskToList(d["image_url"], d["filename"], d["status"], d["current_stage"], d["completion"])
        }
        $('#taskTable').removeClass('loading')
      }
    });


}

listTasks()