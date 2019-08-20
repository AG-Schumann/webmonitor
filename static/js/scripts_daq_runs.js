function LoadRuns() {
    var name = $("#exp_name").val();
    $.getJSON("/control/get_runs/" + name + "/", function(data) {
        var html = "";
        var runs = data['runs'];
        for (var i = 0; i < runs.length; i += 1) {
            html += "<tr class=\"run_row\">";
            html += "<td>" + runs[i]["run_id"] + "</td>";
            html += "<td>" + runs[i]["mode"] + "</td>";
            html += "<td>" + runs[i]["start"] + "</td>";
            html += "<td>" + runs[i]["duration"] + "</td>";
            html += "<td>" + runs[i]["user"] + "</td>";
            html += "<td>" + runs[i]["comment"] + "</td>";
            html += "<td>" + runs[i]["meshes"] + "</td>";
            html += "<td>" + runs[i]["tags"] + "</td>";
            html += "<td>";
            html += "<img src=\"/static/img/mag_glass.png\" alt=\"Details\" onclick=\"ToggleRunDetail(" + i + ")\" class=\"icon\">";
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
        tr[i].style.display =  "";
    }
}

function GenerateStraxList() {
    var rows = $("#runs_table_body").children("tr");
    var ret = "";
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        if (row.style.display == "") {
            var runid = parseInt(row.children[0].innerHTML).toString(16);
            ret += '0'.repeat(4-runid.length) + runid;
        }
    }
    $("#straxlist").html("Runlist: " + ret);
}

function ToggleRunDetail(row) {
    $("#tagdetail").css("display", "none");
    $("#rundetail").css("display", "block");
    var name = $("#exp_name").val();
    var runid = $("#runs_table_body").children("tr").eq(row).children("td:first").html();
    $.getJSON("/control/runs/get_run_detail/" + name + "/" + runid + "/", function(data) {
        if (typeof data.run_id == "undefined") {
            HideTabs();
            return;
        }
        $("#exp_name_h").val(name + "__" + runid);
        $("#d_run_id").html("Run id: " + data['run_id']);
        $("#d_run_mode").html("Run mode: " + data['mode']);
        $("#d_run_start").html("Run start time: " + data['start']);
        $("#d_run_end").html("Run end time: " + data['end']);
        $("#d_run_dur").html("Run duration: " + data['duration']);
        $("#d_run_user").html("Run started by: " + data['user']);
        $("#d_run_comment").val(data['comment']);
        $("#d_run_tags").html("");
        data['tags'].forEach(function(tag) {
            var tn = "rm_" + tag;
            var t = "<input type=\"checkbox\" name=\""+tn+"\" id=\""+tn+"\">";
            t += tag;
            $("#d_run_tags").append("<li>" + t + "</li>");
        });
        $("#d_run_tags").append("<li><input type=\"text\" name=\"newtag\" pattern=\"[a-zA-Z0-9_\\\\-]+\" placeholder=\"some_new_tag\"></li>");
        $("#d_run_data").html("");
        $("#d_run_config").html(JSON.stringify(data['config'], null, '\t'));
    });
}

function ToggleTagDetail() {
    $("#tagdetail").css("display", "block");
    $("#rundetail").css("display", "none");
}

function FilterRunsByTags() {
    var incl_tags = [];
    var excl_tags = [];
    var tag_column = 7;
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
    var tr = $("#runs_table_body").children('tr');
    for (var i = 0; i < tr.length; i++) {
        var td = tr[i].children[tag_column];
        var tags_this_row = td.innerHTML.split(",");
        if (excl_tags.length > 0 && tags_this_row
                    .map(function(tag) {return excl_tags.includes(tag);})
                    .some(function(v) {return v;})) {
            tr[i].style.display = "none";

        } else if (incl_tags.length > 0 && tags_this_row
                    .map(function(tag) {return incl_tags.includes(tag);})
                    .some(function(v) {return v;})) {
            tr[i].style.display = ""
        }
    } // rows.forEach
    HideTabs();
}

function HideTabs() {
    $("#tagdetail").css("display", "none");
    $("#rundetail").css("display", "none");
}
