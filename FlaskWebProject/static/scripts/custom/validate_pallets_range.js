function validate(form) {
    event.preventDefault();

    var CaseCount = form.EndCase.value - form.StartCase.value;

    document.getElementById("print_PalletNumber").innerHTML = form.PalletNumber.value
    document.getElementById("print_ItemNumber").innerHTML = form.ItemNumber.value
    document.getElementById("print_Shift").innerHTML = 'Shift: ' + form.Shift.value
    document.getElementById("print_Date").innerHTML = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    document.getElementById("print_Time").innerHTML = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

    document.getElementById("print_StartCase").innerHTML = 'StartCase: ' + form.StartCase.value
    document.getElementById("print_EndCase").innerHTML = 'EndCase: ' + form.EndCase.value


    var jsonToServer = {
        "ItemNumber": form.ItemNumber.value,
        "PalletNumber" : form.PalletNumber.value,
        "csrf_token" : form.csrf_token.value,
        "CaseCount" : CaseCount
    };

    fetch_validate_pallet_casecount(form,jsonToServer);
}