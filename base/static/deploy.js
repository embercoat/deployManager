function deployArtifact(id){
//id_appServer
    appServer = $("#id_appServer").val();
    window.DeployManager.deploy(id, appServer);
}

$(document).ready(function(){
    $("#searchArtifact").click(function(){
        console.log("searching for artifacts");
        groupid = $("#groupid").val();
        artifactid = $("#artifactid").val();
        results = window.DeployManager.search(groupid, artifactid);
        console.log(results.responseJSON);
        console.log("done searching");

        $.each(results.responseJSON['result'], function(index, item){
            console.log(item['repository']['name']);


            $.each(item['artifacts'], function(index, artifact){
                console.log(artifact['groupid']+':'+artifact['artifactid']+':'+artifact['version']);
                tr = $("");
                $('<tr>' +
                    '<td>'+ item['repository']['name'] +'</td>'+
                    '<td>'+ artifact['groupid']        +'</td>'+
                    '<td>'+ artifact['artifactid']     +'</td>'+
                    '<td>'+ artifact['version']        +'</td>'+
                    '<td><a href="javascript:deployArtifact('+ artifact['id']+')" >Deploy</a></td>' +
                  '</tr>'
                ).appendTo("#foundArtifacts");
            });
        });
    });
});