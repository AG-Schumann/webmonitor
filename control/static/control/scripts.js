// scripts go here
function UpdateStatus(){
    $.getJSON('get_status', function(data) {
        //console.log(data);
        var ret = {'status' : '',
            'buttons' : []
        };
        if (data['status'] === 'offline') {
            ret.status = "Offline";
            ret.buttons = [true, true, true, true];
        } else if (data['status'] === 'idle') {
            ret.status = "Idle";
            ret.buttons = [true,true,false,true];
        } else if (data['status'] === 'arming') {
            ret.status = "Arming for " + data['mode'];
            ret.buttons = [true,true,true,true];
        } else if (data['status'] === 'armed') {
            ret.status = "Armed for " + data['mode'];
            ret.buttons = [false,true,true,false];
        } else if (data['status'] === 'running') {
            ret.status = "Run " + data['name'] + " is live";
            ret.buttons = [true,false,true,true];
        } else if (data['status'] === 'straxinating') {
            ret.status = "Straxinating " + data['name'];
            ret.buttons = [true,true,true,true];
        }
        //console.log(ret);
        $("#statusnow").html(ret.status);
        $("#startbutton").attr("disabled",ret.buttons[0]);
        $("#stopbutton").attr("disabled",ret.buttons[1]);
        $("#armbutton").attr("disabled",ret.buttons[2]);
        $("#disarmbutton").attr("disabled",ret.buttons[3]);
        //return ret;
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
        //console.log('History');
        //console.log(html);
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
        //console.log('Runs');
        //console.log(html);
        $("#runstable").html(html);
        //return html;
        //document.getElementById(runstable).innerHTML=html;
    });
}

