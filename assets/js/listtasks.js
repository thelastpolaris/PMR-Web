'use strict';

function taskRow(task_id, image_url, filename, status, current_stage, completion){
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
                  ${status == 1 ? `<a class="dropdown-item" href="#">Pause</a>` : `<a class="dropdown-item" href="#">Rerun</a>`}
                  <button class="dropdown-item" onclick=deleteTask(${task_id})>Delete</button>
                </div>
              </div>
            </td>
            </tr>`;
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function addTaskToList(task_id, image_url, filename, status, current_stage, completion) {
    $("#taskLists").append(taskRow(task_id, image_url, filename, status, current_stage, completion))
}

var global_current_page = 0

function tasksStartLoading(tasks_per_page) {
    $('#taskLists').css("min-height", tasks_per_page * 100 + "px")
    $('#taskLists').empty()
    $('#taskTable').addClass('loading')
    $('#pagination').hide()
}

function makeActivePageButton(buttons, active_page) {
    for (var i = 0; i < buttons.length; i++) {
        if (i !== active_page) buttons[i].removeClass("active")
        else buttons[i].addClass("active")
    }
}

function tasksFinishLoading(num_all_tasks, current_page, tasks_per_page) {
    $('#taskTable').removeClass('loading')
    $('#taskLists').css("min-height", "0px")
    global_current_page = current_page
    var max_page = Math.ceil(num_all_tasks/tasks_per_page)

    if(num_all_tasks <= tasks_per_page === false) {
        $('#pagination').show()
        if(current_page === 0) $('#leftPage').addClass('disabled')
        else $('#leftPage').removeClass('disabled')

        if((current_page + 1)*tasks_per_page >= num_all_tasks) $('#rightPage').addClass('disabled')
        else $('#rightPage').removeClass('disabled')

        var firstPage = $('#firstPage > button')
        var secondPage = $('#secondPage > button')
        var thirdPage = $('#thirdPage > button')

        console.log(num_all_tasks, tasks_per_page, max_page, current_page)
        var buttons = [$('#firstPage'), $('#secondPage'), $('#thirdPage')]

        if (max_page <= 2) {
            firstPage.hide()
        } else {
            firstPage.show()
        }

        if(max_page - current_page <= 2) {
            if(max_page - current_page === 2) {
                makeActivePageButton(buttons, 1)
            } else if(max_page - current_page === 1) {
                makeActivePageButton(buttons, 2)
            }

            firstPage.html(max_page - 2)
            secondPage.html(max_page - 1)
            thirdPage.html(max_page )
        } else {
            makeActivePageButton(buttons, 0)
            firstPage.html(current_page + 1)
            secondPage.html(current_page + 2)
            thirdPage.html(current_page + 3)
        }
    }
}

function deleteTask(task_id) {
    var formdata = new FormData();

    formdata.append("_xsrf", getCookie("_xsrf"))
    formdata.append("mode", "delete")
    formdata.append("task_id", task_id)
    console.log(task_id)

    $.ajax({
      url: '/',
      data: formdata,
      processData: false,
      contentType: false,
      type: 'POST',
      success: function(data) {
        listTasks(global_current_page)

        $.notify({
                    icon: 'ni ni-check-bold',
                    message: "<b>Success!</b> Task was deleted."
                },
                {
                    type: "success",
                    allow_dismiss: true,
                    placement: {
                        align: "center"
                    },
                });
      }
    });
}

function listTasks(page = 0, tasks_per_page = 3) {
    tasksStartLoading(tasks_per_page)

    var formdata = new FormData();
    formdata.append("_xsrf", getCookie("_xsrf"))
    formdata.append("mode", "list")
    formdata.append("start", page*tasks_per_page)
    formdata.append("amount", tasks_per_page)

    $.ajax({
      url: '/',
      data: formdata,
      processData: false,
      contentType: false,
      type: 'POST',
      success: function(data){
        for (var d of data["tasks"]) {
            addTaskToList(d["task_id"], d["image_url"], d["filename"], d["status"], d["current_stage"], d["completion"])
        }
        tasksFinishLoading(data["num_all_tasks"], page, tasks_per_page)
      }
    });
}

listTasks()