/*
artifactPK
appServerPK
*/

function deploy(artifact, appServer){
    console.log("Deploying "+ artifact + " to server " + appServer);
    $.ajax({
        url : "/api/deploy/deploy",
        type: "POST",
        dataType : "json",
        data : '{"artifactPK" : '+artifact+', "appServerPK" : '+appServer+'}',
        contentType: "application/json"
    });
}

$(document).ready(function () {

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

});