// scripts go here
function UpdateStatus(){
    
    
    $.getJSON('/control/get_status', function(data) {
        var buttons = [];
    	
        if (data['daqstatus'] === 'offline') {
            buttons = [true, true, true];
        } else if (data['daqstatus'] === 'idle') {
            if(data['straxstatus'] == 'idle') {
                buttons = [false, true, false];
            } else {
                buttons = [true, false, true];
            }
        } else if (data['daqstatus'] === 'arming') {
            buttons = [true, true, true];
        } else if (data['daqstatus'] === 'armed') {
            buttons = [false, false, true];
        } else if (data['daqstatus'] === 'running') {
            buttons = [true, false, true];
        } else if (data['daqstatus'] === 'error') {
            buttons = [true, false, true];
        } else {
            buttons = [true, true, true];
        }
        $("#startbutton").attr("disabled", buttons[0]);
        $("#stopbutton").attr("disabled", buttons[1]);
        $("#ledbutton").attr("disabled", buttons[2]);
        
        for (var key in data) {
            if(key === 'daqworklist'){
                if(data[key] == "running"){
                    $("#pausebutton").html("pause");
                } else{
                    $("#pausebutton").html("continue");
                }
            }
                
            if (key === 'runprogress') {
                $("#progress").val(data["runprogress"]);
                if(data["runprogress"] == 0){
                    $("#runprogress_field").html("&nbsp;");
                } else {
                    $("#runprogress_field").html("&nbsp;" +  Math.round(data["runprogress"]) + " / "+ data["run_duration"] +" s");
                } 
                $("#progress").val(data[key]);
                document.getElementById("progress").max=data["run_duration"];
            } else {
                $("#" + key).html(data[key]);
            }
        }
    });
    
    $.getJSON('/control/get_upcoming_runs/xebra/', function(data) {
        $("#upcoming_runs_count").html(data["runs"]);
        $("#upcoming_runs_duration").html(data["duration"]);
    });
}

function UpdateStatusHistory(){
    $.getJSON('/control/get_status_history', function(data) {
        var html = "";
        var d = data['rows'];
        for (var i = 0; i < d.length; i += 1) {
            html += "<tr>";
            html += "<td>" + d[i]['time'] + "</td>";
            html += "<td>" + d[i]['rate'] + "</td>";
            html += "<td>" + d[i]['status'] + "</td>";
            html += "<td>" + d[i]['run_mode'] + "</td>";
            html += "</tr>";
        }
        $("#historytable").html(html);
    });
}

function UpdateRuns(){
    $.getJSON('/control/get_runs/xebra/5', function(data) {
        var html = "";
        var d = data['runs'];
        for (var i = 0; i < d.length; i += 1) {
            html += "<tr>";
            html += "<td>" + d[i]['run_id'] + "</td>";
            html += "<td>" + d[i]['mode'] + "</td>";
            html += "<td>" + d[i]['start'] + '</td>';
            html += "<td>" + d[i]['end'] + '</td>';
            html += "<td>" + d[i]['duration'] + '</td>';
            html += "<td>" + d[i]['user'] + '</td>';
            html += '</tr>';
        }
        $("#runstable").html(html);
    });
}

function UpdateUpcomingRuns(){
    experiment = $("#exp_name").val();
    $.getJSON('/control/list_upcoming_runs/'+experiment+'/', function(data) {
        var html = "";
        var d = data['runs'];
        if( d.length > 0){
            for (var i = 0; i < d.length; i += 1) {
                html += "\n<tr>";
                html += "<td>"
                
                html += "<input id='checkbox_"+i+"' type='checkbox' name='checkbox_to_delete' value='"+d[i]['id']+"'>";
                html += "<label for='checkbox_"+i+"'>" + d[i]['mode'] + "</label>"
                
                html += "</td>";
                html += "<td>" + d[i]['duration'] + "</td>";
                html += "<td>" + d[i]['comment'] + "</td>";
                html += "<td><pre>" + d[i]['config_override'] + "</pre></td>";
                html += "</tr>";
            }
        } else {
            html += "<td colspan='9'>Nothing found</td>"
        }
        $("#runs_table_body").html(html);
    });
}

function ClearUpcomingRuns(){
    experiment = $("#exp_name").val();
    
    $.getJSON('/control/clear_upcoming_runs/'+experiment+'/', function(data){
        
        
        if(data["OK"] == true){
            var html = "experiment cleared";
            $("#runs_table_body").html(html);
            UpdateUpcomingRuns();
        } else if("msg" in data){
            alert(data["msg"])
        } else{
            alert("you do not seem to be authorized")
        }
        
    });
}

function RemoveUpcomingRuns(){
    checkboxes = document.querySelectorAll("input[name=checkbox_to_delete]:checked")
    alert_done = false
    done_all=0
    
    for(var int_checkbox = 0; int_checkbox<checkboxes.length; int_checkbox++){
        checkbox = checkboxes[int_checkbox];
        
        if(checkbox.checked == true){
        
            $.getJSON('/control/clear_a_upcoming_run/'+experiment+'/'+checkbox.value+'/', function(data){
                done_all++
                if(alert_done == false){
                    if(data["OK"] == false){
                        alert_done = true
                        if("msg" in data){
                            alert(data["msg"])
                        } else{
                            alert("you do not seem to be authorized")
                        }
                    }
                }
                
                if(done_all == checkboxes.length){
                    if(alert_done == false){
                        UpdateUpcomingRuns();
                    }
                }
            });
        
        }
    }
    
}


function LoadConfigDoc() {
    var name = $("#mode_select").val();
    $.getJSON('/control/get_cfg_doc/' + name + '/', function(data) {
        $("#name_field").val(data['name']);
        delete data['name'];
        $("#desc_field").val(data['description']);
        delete data['description'];
        $("#user_field").val(data['user']);
        delete data['user'];
        $("#detector_field").val(data['detector']);
        delete data['detector'];
        if ("includes" in data) {
            $("#include_field").val(data['includes']);
            delete data['includes'];
        } else {
            $("#include_field").val("");
        }
        $("#content_field").val(JSON.stringify(data, null, 4));
    });
}


