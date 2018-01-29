

window.DeployManager = {
    deploy : function(artifact, appServer){
        console.log("Deploying "+ artifact + " to server " + appServer);
        $.ajax({
            url : "/api/deploy/deploy",
            type: "POST",
            dataType : "json",
            data : '{"artifactPK" : '+artifact+', "appServerPK" : '+appServer+'}',
            contentType: "application/json"
        });
    },
    undeploy : function(deployment){
        $.ajax({
            url : "/api/deploy/undeploy",
            type: "POST",
            dataType : "json",
            data : '{"deployment" : '+deployment+'}',
            contentType: "application/json"
        });
    },
    search : function(groupid, artifactid, version){
        version = version || "";
        return $.ajax({
            url : "/api/search/artifact",
            type: "POST",
            dataType : "json",
            data : '{"groupid" : "'+groupid+'", "artifactid" : "'+artifactid+'", "version": "'+version+'"}',
            contentType: "application/json",
            async: false
        });
    }
};