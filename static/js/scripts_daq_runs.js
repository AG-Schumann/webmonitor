function LoadRuns() {
    var name = $("#exp_name").val();
    $.getJSON("/control/get_runs/" + name + "/", function(data) {
        var html = "";
        var runs = data['runs'];
        for (var i = 0; i < runs.length; i += 1) {
            html += "<tr>";
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
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
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
        tr[i].style.display = "";
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

function TabSelect() {
    var inc_with_input = [];
    var exc_with_input = [];
}
