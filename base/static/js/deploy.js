function addLogLine(message, date){
    $(
        "<li>"+message+"</li>"
    ).prependTo("#taskLog");
}
function pollUpdates(data){
    console.log(data);
    var taskID = data.task;
    fulltask = window.DeployManager.fullTask(taskID);
    $("#deploymentModal").modal("hide");
    $("#statusModal").modal();
    $("#taskLog").empty();
    $("#deploymentProgressbar").addClass('progress-bar progress-bar-striped progress-bar-animated');
    $("#statusModalLabel").html("Working...");

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
        if(window.DeployManager.status(taskID) === window.DeployManager.taskStatus.COMPLETED){
            clearInterval(intervalId);
            $("#deploymentProgressbar").addClass('bg-success')
                                       .removeClass('progress-bar-striped')
                                       .removeClass('progress-bar-animated');
            $("#statusModalLabel").html("Complete");
        }
    }, 2000);
}


function deployArtifact(){
//id_appServer
    artifactid = $("#modal_artifactid").val();
    appServer = $("#modal_appserver").val();
    window.DeployManager.deploy(artifactid, appServer, pollUpdates);
}

$(document).ready(function(){
    $("#searchArtifact").click(function(){
        console.log("searching for artifacts");
        groupid = $("#groupid").val();
        artifactid = $("#artifactid").val();
        results = window.DeployManager.search(groupid, artifactid);
        console.log(results.responseJSON);
        console.log("done searching");
        $("#foundArtifacts").empty();
        $.each(results.responseJSON['result'], function(index, item){
            console.log(item['repository']['name']);


            $.each(item['artifacts'], function(index, artifact){
                console.log(artifact['groupid']+':'+artifact['artifactid']+':'+artifact['version']);
                fullArtifact = artifact['groupid']+':'+artifact['artifactid']+':'+artifact['version'];
                tr = $("");
                $('<tr>' +
                    '<td>'+ item['repository']['name'] +'</td>'+
                    '<td>'+ artifact['groupid']        +'</td>'+
                    '<td>'+ artifact['artifactid']     +'</td>'+
                    '<td>'+ artifact['version']        +'</td>'+
                    '<td><a class="btn btn-info" data-artifactid="'+ artifact['id']+'" data-artifact="'+fullArtifact+'" data-toggle="modal" data-target="#deploymentModal">Deploy...</a></td>' +
                  '</tr>'
                ).appendTo("#foundArtifacts");
            });
        });
    return false;
    });
    $('#deploymentModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var artifactid = button.data('artifactid');
        var artifactName = button.data('artifact');
        var modal = $(this);
        modal.find('.modal-body #modal_artifactName').val(artifactName);
        modal.find('.modal-body #modal_artifactid').val(artifactid);
    });
});