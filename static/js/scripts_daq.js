// scripts go here
function UpdateStatus(){
    $.getJSON('get_status', function(data) {
        var stat = "";
        var buttons = [];
        if (data['status'] === 'offline') {
            stat = "Offline";
            buttons = [true, true, true, true];
        } else if (data['status'] === 'idle') {
            stat = "Idle";
            buttons = [true, true, false, false];
        } else if (data['status'] === 'arming') {
            stat = "Arming for " + data['mode'];
            buttons = [true, true, true, true];
        } else if (data['status'] === 'armed') {
            stat = "Armed for " + data['mode'];
            buttons = [false, true, true, true];
        } else if (data['status'] === 'running') {
            stat = "Run " + data['name'] + " is live";
            buttons = [true, false, true, true];
        } else if (data['status'] === 'error') {
            stat = "Error";
            buttons = [true, false, true, true];
        } else {
            stat = "Unknown";
            buttons = [true, true, true, true];
        }
        $("#statusnow").html(stat);
        $("#startbutton").attr("disabled", buttons[0]);
        $("#stopbutton").attr("disabled", buttons[1]);
        $("#armbutton").attr("disabled", buttons[2]);
        $("#ledbutton").attr("disabled", buttons[3]);
    });
}

function UpdateStatusHistory(){
    $.getJSON('get_status_history', function(data) {
        var html = "";
        var t = data['time'];
        var r = data['rate'];
        var f = data['freq'];
        for (var i = 0; i < t.length; i += 1) {
            html += "<tr>";
            html += "<td>" + t[i] + "</td>";
            html += "<td>" + r[i] + "</td>";
            html += "<td>" + f[i] + "</td>";
            html += "</tr>";
        }
        $("#historytable").html(html);
    });
}

function UpdateRuns(){
    $.getJSON('get_runs', function(data) {
        var html = "";
        var d = data['runs'];
        for (var i = 0; i < data['runs'].length; i += 1) {
            html += "<tr>";
            html += "<td>" + d[i]['number'] + "</td>";
            html += "<td>" + d[i]["name"] + "</td>";
            html += "<td>" + d[i]['mode'] + "</td>";
            html += "<td>" + d[i]['start'] + '</td>';
            html += "<td>" + d[i]['end'] + '</td>';
            html += "<td>" + d[i]['duration'] + '</td>';
            html += '</tr>';
        }
        $("#runstable").html(html);
    });
}

