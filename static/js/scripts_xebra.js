function PopulateReadingDropdown(chartnum, sensor_name) {
    // called in trend
    console.log('Got ' + sensor_name);
    $.getJSON('/xebra/getreadings/'+sensor_name+'/', function(data) {
        var html = "<option value=''>select reading</option>";
        for (var i = 0; i < data['readings'].length; i += 1) {
            html += "<option value='"+i+"'>"+data['readings'][i]+"</option>";
        }
        $("#chart"+chartnum+"reading").html(html);
    });
}

function GetReadingDetails(sensor_name, reading_name) {
    // called in detail
    console.log('Getting details for ' + sensor_name + ' ' + reading_name);
    if (reading_name.length == 0) {
        $("#rd_legend").html("No reading selected");
        $("#rd_alarm_list").html("");
        $("#rd_cfg_list").html("");
        $("#rd_runmode").html("");
        $("#rd_status").html("");

        $("#rd_name").val("");
        $("#rd_alrec").val("");
        $("#rd_roi").val("");
        return;
    }
    $.getJSON('/xebra/get_reading_detail/' + sensor_name + '/' + reading_name + '/', function(data) {
        if (data['html']) {
            for (var key in data['html']) {
                $("#" + key).html(data['html'][key]);
            }
            for (var key in data['value']) {
                $("#" + key).val(data['value'][key]);
            }
        }
    });
}

function LoadSensorDetails(sensor_name) {
    // called in detail
    console.log('Getting details for ' + sensor_name);
    if (sensor_name.length == 0) {
        $("#s_name_startstop").val("");
        $("#status_legend").html("Current sensor status: unknown");
        $("#startbtn").attr("disabled", true);
        $("#rdbtn").attr("disabled", true);
        $("#addrbtn").attr("disabled", true);
        $("#subtitle").html('Sensor detail:');
        $("#s_name_rd").val("");
        $("#reading_dropdown").html('<option value="" selected>Select reading</option>');

        $("#s_name_addr").val("");
        $("#address_block").html("No address info!");
        return;
    }
    $.getJSON('/xebra/get_sensor_details/' + sensor_name + '/', function(data) {
        if (data['html']) {
            for (var key in data['html']) {
                $("#" + key).html(data['html'][key]);
            }
            for (var key in data['value']) {
                $("#" + key).val(data['value'][key]);
            }
            $("#startbtn").attr("disabled", false);
            $("#rdbtn").attr("disabled", false);
            $("#addrbtn").attr("disabled", false);
            GetReadingDetails("none","");
        }
    });
}

function LoadHostSettings(host_name) {
    //called in detail
    console.log('Getting details for ' + host_name);
    if (host_name.length == 0) {
        $("#sysmon_timer").val("");
        return;
    }
    $.getJSON('/xebra/get_host_detail/' + host_name + '/', function(data) {
        for (var key in data['html']) {
                $("#" + key).html(data['html'][key]);
                console.log(key + ' ' + data['html'][key]);
            }
            for (var key in data['value']) {
                $("#" + key).val(data['value'][key]);
                console.log(key + ' ' + data['value'][key]);
            }
        $("#xebra_hostbtn").attr("disabled", false);
        });
}

function UpdateOverview() {
    // called in index
    $.getJSON('/xebra/getoverview', function(data) {
        for (var key in data) {
            $("#" + key).html(data[key]);
        }
    });
}

function UpdateLogs() {
    // called in index
    $.getJSON('/xebra/getlogs', function(data) {
        var html = '';
        var docs = data['docs'];
        for (var i = 0; i < docs.length; i += 1) {
            html += "<tr><td>" + docs[i]['when'] + "</td>";
            html += "<td>" + docs[i]['level'] + "</td>";
            html += "<td>" + docs[i]['name'] + "</td>";
            html += "<td>" + docs[i]['message'] + "</td></tr>";
        }
        $("#logtable").html(html);
    });
}

function UpdateAlarms() {
    // called in index
    $.getJSON('/xebra/getalarms', function(data) {
        var html = '';
        var docs = data['docs'];
        for (var i = 0; i < docs.length; i += 1) {
            html += "<tr><td>" + docs[i]['when'] + "</td>";
            html += "<td>" + docs[i]['message'] + "</td></tr>";
        }
        $("#alarmtable").html(html);
    });
}

function UpdateShift(ev) {
    if (new Date() > ev.start) {
        return;
    }
    $("#shift_modal").css("display", "block");
    var start = ev.start.toISOString().slice(0,10);
    $.getJSON('/xebra/get_shift_detail/' + start + '/', function(data) {
        if (!data) {
            return;
        }
        $("#shift_start").html(data['start']);
        $("#shift_end").html(data['end']);
        if (data['primary'] != '') {
            $("#primary_sel option:contains(" + data['primary'] + ")").prop({selected: true});
            $("#primary_sel option.first").prop({selected: false});
        }
        if (data['secondary1'] != '') {
            $("#secondary1_sel option:contains(" + data['secondary1'] + ")").prop({selected: true});
            $("#secondary1_sel option.first").prop({selected: false});
        }
        if (data['secondary2'] != '') {
            $("#secondary2_sel option:contains(" + data['secondary2'] + ")").prop({selected: true});
            $("#secondary2_sel option.first").prop({selected: false});
        }
    });
}

function CloseModal() {
    $("#shift_modal").css("display", "none");
}
