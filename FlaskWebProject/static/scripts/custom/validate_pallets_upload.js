function validate(form) {
    event.preventDefault();

    var today = new Date();

    var re = new RegExp("0010895611002[0-9][0-9][0-9][0-9][0-9][0-9][0-9]");

    if (!re.test(form.PalletNumber.value))  {
        toastr.error(form.PalletNumber.value + " doesnt not match the required format: 0010895611002#######")
    } else {

        document.getElementById("print_PalletNumber").innerHTML = form.PalletNumber.value
        document.getElementById("print_ItemNumber").innerHTML = form.ItemNumber.value
        document.getElementById("print_Shift").innerHTML = 'Shift: ' + form.Shift.value
        document.getElementById("print_Date").innerHTML = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
        document.getElementById("print_Time").innerHTML = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

        var CaseCodes = []

        for (var field of form.cases) {
            if (field.value > 0) {
                CaseCodes.push(field.value)
                document.getElementById("print_" + field.id).innerHTML = field.value
            }
        }

        var CaseCount = CaseCodes.length
        var uniques = new Set(CaseCodes)

        if (uniques.size != CaseCount) {
            toastr.error("A case barcode is used more than once, please review");
        } else if (CaseCount == 0) {
            toastr.error("Must input case barcodes");
        } else {
            var jsonToServer = {
                "ItemNumber": form.ItemNumber.value,
                "PalletNumber" : form.PalletNumber.value,
                "csrf_token" : form.csrf_token.value,
                "CaseCount" : CaseCount,
                "CaseCodes" : CaseCodes
            };

            fetch_validate_pallet_casecount(form,jsonToServer);
        }
    }
}