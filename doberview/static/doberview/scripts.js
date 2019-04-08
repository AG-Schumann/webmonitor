var default_names = ['cryocon_22c__0/cryocon_22c__1/cryocon_22c__2/',
    'Teledyne__0/', 'iseries1__0/'];

function PopulateReadingDropdown(chartnum, sensor_name) {
    // called in trend
    console.log('Got ' + sensor_name);
    $.getJSON('getreadings/'+sensor_name+'/', function(data) {
        var html = "<option value=''>select reading</option>";
        for (var i = 0; i < data['readings'].length; i += 1) {
            html += "<option value='"+i+"'>"+data['readings'][i]+"</option>";
        }
        $("#chart"+chartnum+"reading").html(html);
    });
}

function SetUserChart(chartnum, sensor_name, reading_i) {
    // called in trend
    var name = sensor_name + "__" + reading_i;
    $('#chartu' + chartnum + '_name').html(name);
    DrawChart(chartnum, name);
}

function UpdateCharts() {
    // called in trend
    for (var i = 0; i < 3; i += 1) {
        $.getJSON('getdata/' + default_names[i], function(data) {
            var elem_name = "chartd" + i;
            $("#" + elem_name).data = data['data'];
            $("#" + elem_name).layout = data['layout'];
            Plotly.redraw(elem_name);
        });
        if ($("#chartu" + i + "_name").html() != "None") {
            $.getJSON('getdata/' + $("#chartu" + i + "_name") + '/', function(data) {
                var elem_name = "chartu" + i;
                $("#" + elem_name).data = data['data'];
                $("#" + elem_name).layout = data['layout'];
                Plotly.redraw(elem_name);
            });
        }
    }
}

function DrawCharts() {
    // called in trend
    // can't forloop because fuck javascript
    $.getJSON('getdata/' + default_names[0], function(data) {
        var elem_name = 'chartd0';
        Plotly.newPlot(elem_name, data['data'], data['layout'], data['config']);
    });
    $.getJSON('getdata/' + default_names[1], function(data) {
        var elem_name = 'chartd1';
        Plotly.newPlot(elem_name, data['data'], data['layout'], data['config']);
    });
    $.getJSON('getdata/' + default_names[2], function(data) {
        var elem_name = 'chartd2';
        Plotly.newPlot(elem_name, data['data'], data['layout'], data['config']);
    });
}

function DrawChart(chartid, name) {
    // called in trend
    $.getJSON('getdata/' + name + '/', function(data) {
        var elem_name = "chartu" + chartid;
        Plotly.newPlot(elem_name, data['data'], data['layout'], data['config']);
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
    $.getJSON('get_reading_detail/' + sensor_name + '/' + reading_name + '/', function(data) {
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
    $.getJSON('get_sensor_details/' + sensor_name + '/', function(data) {
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

function UpdateOverview() {
    // called in index
    $.getJSON('getoverview', function(data) {
        for (var key in data) {
            $("#" + key).html(data[key]);
        }
    });
}

function UpdateLogs() {
    // called in index
    $.getJSON('getlogs', function(data) {
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
    $.getJSON('getalarms', function(data) {
        var html = '';
        var docs = data['docs'];
        for (var i = 0; i < docs.length; i += 1) {
            html += "<tr><td>" + docs[i]['when'] + "</td>";
            html += "<td>" + docs[i]['name'] + "</td>";
            html += "<td>" + docs[i]['message'] + "</td></tr>";
        }
        $("#alarmtable").html(html);
    });
}
