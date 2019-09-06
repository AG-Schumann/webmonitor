var status_map = {"stat" : ["On", "Ramping up", "Ramping down", "Overcurrent",
    "Overvoltage", "External trip", "Max voltage", "External disable", "Internal trip",
    "Calibration error", "Unplugged"],
    "pon" : ["En", "Dis"],
    "pdn" : ["Ramp", "Kill"],
    "pw" : ["On", "Off"],
};

var pon_status = ["En", "Dis"];

var pdn_status = ["Ramp", "Kill"];

var pw_status = ["On", "Off"];

function UpdatePMTTable(speed) {
    var int_quantities = ["pon", "pdn", "pw", "stat"];
    $.getJSON('/doberview/get_pmt_status/' + speed + "/", function(data) {
        for (var key in data) {
            var res = key.split("_"); // key_ch
            var quantity = res[0];
            var ch = res[1];
            var value = data[key];
            if (int_quantities.includes(quantity)) {
                $("#ch" + ch + "_" + quantity).html(status_map[quantity][value]);
            } else {
                $("#ch" + ch + "_" + quantity).html(value);
            }
        }
    });
}


