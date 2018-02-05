

window.DeployManager = {
    deploy : function(artifact, appServer, callback){

        console.debug("Deploying "+ artifact + " to server " + appServer);
        call = $.ajax({
            url : "/api/deploy/deploy",
            type: "POST",
            dataType : "json",
            data : '{"artifactPK" : '+artifact+', "appServerPK" : '+appServer+'}',
            contentType: "application/json"
        });
        if(callback !== undefined)
            call.done(callback);
    },
    undeploy : function(deployment, callback){
        console.debug("Undeploying "+ deployment);
        console.log(callback);
        call = $.ajax({
            url : "/api/deploy/undeploy",
            type: "POST",
            dataType : "json",
            data : '{"deployment" : '+deployment+'}',
            contentType: "application/json"
        });
        if(callback !== undefined)
            call.done(callback);

    },
    search : function(groupid, artifactid, version){
        console.debug("Searching for "+groupid+":"+artifactid+":"+version);
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