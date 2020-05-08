function validate(form) {
    event.preventDefault();
    var selected = document.getElementById("ItemNumber").value;
    var PalletNumber = document.getElementById("PalletNumber").value;
    csrf_token = document.getElementById("csrf_token").value
    jsonToServer = {
        'ItemNumber':selected
    }

    fetch(`${window.origin}/fetch/lookuppalletexisting`, {
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

                if (data.PalletExistingCount > 0) {
                    toastr.error(PalletNumber + " already exists, it has " + data.PalletExistingCount + " cases assigned to it")
                } else {
                    console.log("about to submit")
                    document.getElementById("submit-button").click();
                }

            });
          })
          .catch(function (error) {
            console.log("Fetch error: " + error);
          });

}

window.onload = getpalletcounts;
function getpalletcounts() {
    var selected = document.getElementById("ItemNumber").value;
    csrf_token = document.getElementById("csrf_token").value
    jsonToServer = {
        'ItemNumber':selected
    }

    fetch(`${window.origin}/fetch/lookuppalletcount`, {
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

                var html = '<hr><label for="InsertQuantity">Auto upload case count:</label><input name = "InsertQuantity" value="'+ data.requiredCount + '" readonly></input><hr>';
                document.getElementById("ValidationPalletCounts").innerHTML = html;

            });
          })
          .catch(function (error) {
            console.log("Fetch error: " + error);
          });

}