

window.DeployManager = {
    taskStatus : {
        "NEW"       : 0,
        "RUNNING"   : 1,
        "COMPLETED" : 2,
        "FAILED"    : 3,
        "ABORTED"   : 4,
    },
    statusFromInt : function(status){
        for (key in window.DeployManager.taskStatus) {
            if(window.DeployManager.taskStatus[key] === status)
                return key;
        }
    },
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
    },
    fullTask : function(taskID){
        console.debug("Getting fulltask for: "+taskID);
        return $.ajax({
            url : "/api/task/fullTask",
            type: "POST",
            dataType : "json",
            data : '{"taskID" : "'+taskID+'"}',
            contentType: "application/json",
            async: false
        }).responseJSON;
    },
    logSince : function(taskID, lastLogId){
        console.debug("Getting logSince for: "+taskID +" and logs sice id: "+lastLogId);
        return $.ajax({
            url : "/api/task/logSince",
            type: "POST",
            dataType : "json",
            data : '{"taskID" : "'+taskID+'", "logID" : "'+lastLogId+'"}',
            contentType: "application/json",
            async: false
        }).responseJSON;
    },
    status : function(taskID){
        console.debug("Getting status for: "+taskID);
        return $.ajax({
            url : "/api/task/status",
            type: "POST",
            dataType : "json",
            data : '{"taskID" : "'+taskID+'"}',
            contentType: "application/json",
            async: false
        }).responseJSON.status;
    }
};