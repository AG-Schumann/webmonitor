function LoadRuns() {
    var name = $("#exp_name").val();
    $.getJSON("/control/get_runs/" + name + "/", function(data) {
        var html = "";
        var runs = data['runs'];
        for (var i = 0; i < runs.length; i += 1) {
            html += "<tr onclick=\"ToggleRunDetail(" + i + ")\">";
            html += "<td>" + runs[i]["run_id"] + "</td>";
            html += "<td>" + runs[i]["mode"] + "</td>";
            html += "<td>" + runs[i]["start"] + "</td>";
            html += "<td>" + runs[i]["duration"] + "</td>";
            html += "<td>" + runs[i]["user"] + "</td>";
            html += "<td>" + runs[i]["comment"] + "</td>";
            html += "<td>" + runs[i]["meshes"] + "</td>";
            html += "<td>" + runs[i]["tags"] + "</td>";
            html += "<td>";
            html += "<img src=\"/static/img/mag_glass.png\" alt=\"Details\" onclick=\"RunDetail(" + i + ")\" class=\"icon\">";
            html += "<img src=\"/static/img/remove_btn.png\" alt=\"Remove\" onclick=\"RemoveRow(" + i + ")\" class=\"icon\">";
            html += "</td>";
            html += "</tr>";
        }
        $("#runs_table_body").html(html);
    });
}

function RemoveRow(i) {
    $("#runs_table_body").children("tr")[i].style.display = "none";
}

function FilterRunsTable(column) {
    var tr = $("#runs_table_body").children("tr");
    var re = $("#runs_columns").find("input").eq(column).val();
    try {
        var regex = new RegExp(re);
    } catch(err) {
        return;
    }

    for (var i = 0; i < tr.length; i++) {
        var td = tr.eq(i).children("td").eq(column);
        if (td) {
            if (regex.test(td.html())) {
                tr[i].css("display", "");
            } else {
                tr[i].css("display", "none");
            }
        } else {
            console.log('No td');
        }
    }
}

function ResetTable() {
    var table = $("#runs_table_body");
    var tr = table.children("tr");
    $("#runs_columns").find("input").val("");
    for (var i = 0; i < tr.length; i++) {
        tr[i].css("display", "");
    }
}

function GenerateStraxList() {
    var rows = $("#runs_table_body").children("tr");
    var ret = "";
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        if (row.css("display") == "") {
            var runid = parseInt(row.children[0].innerHTML).toString(16);
            ret += '0'.repeat(4-runid.length) + runid;
        }
    }
    $("#straxlist").html("Runlist: " + ret);
}

function ToggleRunDetail(row) {
    $("#tablediv").css("width", "70%");
    $("#tagdetail").css("display", "");
    var name = $("#exp_name").val();
    var row = $("#runs_table_body").children("tr").eq(row).children("td:first").html();
    $.getJSON("/control/get_run_detail/" + name + "/" + runid + "/", function(data) {
        if (!data) {
            return;
        }
        $("#exp_name").val(name + "__" + runid);
        $("#d_run_id").html("Run id: " + data['run_id']);
        $("#d_run_mode").html("Run mode: " + data['mode']);
        $("#d_run_start").html("Run start time: " + data['start']);
        $("#d_run_end").html("Run end time: " + data['end']);
        $("#d_run_dur").html("Run duration: " + data['duration']);
        $("#d_run_user").html("Run started by: " + data['user']);
        $("#d_run_tags").html("");
        data['tags'].forEach(function(tag) {
            var tn = "rm_" + tag;
            var t = "<input type=\"checkbox\" name=\""+tn+"\" id=\""+tn"\"";
            t += "<label for=\"rm_" + tag + "\">Remove?</label>";
            t += tag
            $("#d_run_tags").append("<li>" + tag + "</li>");
        });
        $("#d_run_tags").append("<li><input type=\"text\" name=\"newtag\" pattern=\"[a-zA-Z0-9_\\\\-]\" placeholder=\"some_new_tag\"></li>");
        $("#d_run_data").html("");
        data['data'].forEach(function(entry) {
            $("#d_run_data").append("<li>" + entry['type'] + ": " + entry['size']  + " MB</li>");
        });
        $("#d_run_config").html(JSON.stringify(data['config'], null, '    '));
    });
}

function FilterRunsByTags() {
    var incl_tags = [];
    var excl_tags = [];
    var tag_column = 7;
    //$("#includetags").children("li").filter(function(li) {
    //    return li.children("input:first").val() != "";
    //}).map(function(li) {return li.children("input:first").val();});
    for (var i = 0; i < 4; i++) {
        var v = $("#includetags").children("li").eq(i).children("input:first").val();
        if (v != "") {
            incl_tags.push(v);
        }
        v = $("#excludetags").children("li").eq(i).children("input:first").val();
        if (v != "") {
            excl_tags.push(v);
        }
    }
    $("#runs_table_body").children("tr").each(function(idx, row) {
        var tags_this_row = row.children("td").eq(tag_column).split(",");
        var incl = true;
        var excl = false;
        tags_this_row.forEach(function(tag) {
            excl = excl || excl_tags.includes(tag);
            incl = incl && incl_tags.includes(tag);
        }); // tags.forEach
        var hide = !(incl && !excl);
        if (hide) {
            row.style("display","none");
        }
    }); // rows.forEach
}

function HideTabs() {
    $("#tagdetail").css("display", "none");
    $("#rundetail").css("display", "none");
    $("#runstablediv").css("width", "100%");
}
