function validate(form) {
    event.preventDefault();

    var CaseCount = form.EndCase.value - form.StartCase.value;

    var jsonToServer = {
        "ItemNumber": form.ItemNumber.value,
        "PalletNumber" : form.PalletNumber.value,
        "csrf_token" : form.csrf_token.value,
        "CaseCount" : CaseCount
    };

    fetch_validate_pallet_casecount(form,jsonToServer);
}