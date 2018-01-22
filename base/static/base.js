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
function undeploy(deployment){
    $.ajax({
        url : "/api/deploy/undeploy",
        type: "POST",
        dataType : "json",
        data : '{"deployment" : '+deployment+'}',
        contentType: "application/json"
    });
}
