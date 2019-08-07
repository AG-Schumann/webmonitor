// scripts go here
function UpdateStatus(){
    $.getJSON('/control/get_status', function(data) {
        var buttons = [];
        if (data['daqstatus'] === 'offline') {
            buttons = [true, true, true, true];
        } else if (data['daqstatus'] === 'idle') {
            buttons = [true, true, false, false];
        } else if (data['daqstatus'] === 'arming') {
            buttons = [true, true, true, true];
        } else if (data['daqstatus'] === 'armed') {
            buttons = [false, false, true, true];
        } else if (data['daqstatus'] === 'running') {
            buttons = [true, false, true, true];
        } else if (data['daqstatus'] === 'error') {
            buttons = [true, false, true, true];
        } else {
            buttons = [true, true, true, true];
        }
        $("#startbutton").attr("disabled", buttons[0]);
        $("#stopbutton").attr("disabled", buttons[1]);
        $("#armbutton").attr("disabled", buttons[2]);
        $("#armresetbtn").attr("disabled", buttons[2]);
        $("#ledbutton").attr("disabled", buttons[3]);
        for (var key in data) {
            $("#" + key).html(data[key]);
        }
    });
}

function UpdateStatusHistory(){
    $.getJSON('/control/get_status_history', function(data) {
        var html = "";
        console.log(data);
        var d = data['rows'];
        for (var i = 0; i < d.length; i += 1) {
            html += "<tr>";
            html += "<td>" + d[i]['time'] + "</td>";
            html += "<td>" + d[i]['rate'] + "</td>";
            html += "<td>" + d[i]['status'] + "</td>";
            html += "<td>" + d[i]['run_id'] + "</td>";
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
