
function fetch_validate_pallet_casecount(form,jsonToServer) {
    var csrf_token = jsonToServer['csrf_token']
    var ItemNumber = jsonToServer['ItemNumber']
    var PalletNumber = jsonToServer['PalletNumber']
    var CaseCount = jsonToServer['CaseCount']

    fetch(`${window.origin}/fetch/validatepallet`, {
          method: "POST",
          credentials: "include",
          body: JSON.stringify(jsonToServer),
          cache: "no-cache",
          headers: new Headers({
            "content-type": "application/json",
            "X-CSRFToken": csrf_token
          })
        })
          .then(function (response) {
            if (response.status !== 200) {
              console.log(`Looks like there was a problem. Status code: ${response.status}`);
              return;
            }
            response.json().then(function (data) {
              if (data.requiredCount != CaseCount) {
                toastr.info(ItemNumber + " requires case count: " + data.requiredCount)
                toastr.error("Total case count is: " + CaseCount);
              } else if (data.PalletExistingCount > 0) {
                toastr.error(PalletNumber + " already exists, it has " + data.PalletExistingCount + " cases assigned to it")
              } else if ("Pallet" in data.ExistingPalletAssignment) {
                toastr.error("CaseCode " + data.ExistingPalletAssignment['CaseBarcode'] + " already exists, it is assigned to " + data.ExistingPalletAssignment['Pallet'])
              } else {
                getbarcode(csrf_token,PalletNumber)
                setTimeout(function(){print()}, 1000);
                setTimeout(function(){document.getElementById("submit-button").click();}, 2000);

              };

            });
          })
          .catch(function (error) {
            console.log("Fetch error: " + error);
          });

}