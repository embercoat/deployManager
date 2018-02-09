function deployArtifact(){
//id_appServer
    artifactid = $("#modal_artifactid").val();
    appServer = $("#modal_appserver").val();
    window.DeployManager.deploy(artifactid, appServer, callbackPollUpdates);
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