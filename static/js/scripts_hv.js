var status_map = {"stat" : ["On", "Ramping up", "Ramping down", "Overcurrent", "Undercurrent",
    "Overvoltage", "External trip", "Max voltage", "External disable", "Internal trip",
    "Calibration error", "Unplugged"],
    "pon" : ["Dis", "En"],
    "pdn" : ["Kill", "Ramp"],
    "pw" : ["Off", "On"],
};
var is_form_num = {"stat" : false, "vmon" : false, "setp" : true, "pw" : false,
    "imon" : false, "tripi" : true, "tript" : true, "rup" : true, "rdn" : true,
    "pon" : false, "pdn" : false};
var is_form_sel = {"stat" : false, "vmon" : false, "setp" : false, "pw" : true,
    "imon" : false, "tripi" : false, "tript" : false, "rup" : false, "rdn" : false,
    "pon" : true, "pdn" : true};
var pon_status = ["Dis", "En"];
var pdn_status = ["Kill", "Ramp"];
var pw_status = ["Off", "On"];
var int_quantities = ["pon", "pdn", "pw", "stat"];

function UpdatePMTTable(speed) {
    $.getJSON('/xebra/get_pmts/' + speed + "/", function(data) {
        $(":selected").prop({selected: false});
        for (var key in data) {
            var res = key.split("_"); // quant_ch
            var quantity = res[0];
            var ch = res[1];
            var formid = "#ch" + ch + "_" + quantity;
            var value = data[key];
            if (int_quantities.includes(quantity)) {
                if (quantity == 'stat') {
                   var bits = value.toString(2);
                   value = "Off";
                   for (var i=0; i<bits.length; ++i) {
                        if (bits[i] == 1){
                            value = status_map[quantity][i];
                        }
                    }
                } else {
                    value = status_map[quantity][value];
                }
            }
            if (is_form_num[quantity]) {
               $(formid).val(value);
            } else if (is_form_sel[quantity]) {
                $(formid + " option:contains(" + value + ")").prop({selected: true});
            } else {
                $(formid).html(value);
            }
        }
    });
}

