function validate(form) {
    event.preventDefault();

    var CaseCodes = []

    for (var field of form.cases) {
        if (field.value > 0) {
            CaseCodes.push(field.value)
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