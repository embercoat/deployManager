function addLogLine(message, date){
    $(
        "<li>"+message+"</li>"
    ).prependTo("#taskLog");
}
function callbackPollUpdates(data){
    pollUpdates(data.task);
}
function pollUpdates(taskID){
    fulltask = window.DeployManager.fullTask(taskID);
    console.log(fulltask);
    $("#taskLog").empty();
    $("#deploymentProgressbar").addClass('progress-bar progress-bar-striped progress-bar-animated')
                               .removeClass('bg-success');
    $("#statusModalLabel").html(window.DeployManager.statusFromInt(fulltask.task.fields.status));
    $('.modal').modal('hide');
    $("#statusModal").modal();

    lastLogID = 0;
    $.each(fulltask.log, function(key, item){
        addLogLine(item.fields.message);
        if(item.pk > lastLogID)
            lastLogID = item.pk
    });
    intervalId = setInterval(function(){
        logSince = window.DeployManager.logSince(taskID, lastLogID);
        $.each(logSince.log, function(key, item){
            addLogLine(item.fields.message);
            if(item.pk > lastLogID)
                lastLogID = item.pk
        });
        taskStatus = window.DeployManager.status(taskID)
        if(taskStatus === window.DeployManager.taskStatus.COMPLETED){
            clearInterval(intervalId);
            $("#deploymentProgressbar").addClass('bg-success')
                                       .removeClass('progress-bar-striped')
                                       .removeClass('progress-bar-animated');
            $("#statusModalLabel").html(window.DeployManager.statusFromInt(taskStatus));
        }
    }, 2000);
}