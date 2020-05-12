function validate(form) {
    event.preventDefault();

    var CaseCount = form.EndCase.value - form.StartCase.value + 1;

    var re = new RegExp("^0010895611002[0-9][0-9][0-9][0-9][0-9][0-9][0-9]$");

    if (!re.test(form.PalletNumber.value))  {
        toastr.error(form.PalletNumber.value + " doesnt not match the required format: 0010895611002#######")
    } else {

        var today = new Date();
        document.getElementById("print_PalletNumber").innerHTML = form.PalletNumber.value
        document.getElementById("print_ItemNumber").innerHTML = form.ItemNumber.value
        document.getElementById("print_Shift").innerHTML = 'Shift: ' + form.Shift.value
        document.getElementById("print_Date").innerHTML = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
        document.getElementById("print_Time").innerHTML = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

        document.getElementById("print_StartCase").innerHTML = 'StartCase: ' + form.StartCase.value
        document.getElementById("print_EndCase").innerHTML = 'EndCase: ' + form.EndCase.value


        var StartCase = form.StartCase.value
        var EndCase = form.EndCase.value
        var CaseCodes = []

        while (StartCase <= EndCase) {
            CaseCodes.push("Range" + StartCase)
            StartCase ++
        }

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