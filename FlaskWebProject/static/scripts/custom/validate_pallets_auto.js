function validate(form) {
    event.preventDefault();
    var selected = document.getElementById("ItemNumber").value;
    var PalletNumber = document.getElementById("PalletNumber").value;

    var re = new RegExp("0010895611002[0-9][0-9][0-9][0-9][0-9][0-9][0-9]");


    if (!re.test(PalletNumber))  {
        toastr.error(PalletNumber + " doesnt not match the required format: 0010895611002#######")
    } else {

        var today = new Date();
        document.getElementById("print_PalletNumber").innerHTML = form.PalletNumber.value
        document.getElementById("print_ItemNumber").innerHTML = form.ItemNumber.value
        document.getElementById("print_Shift").innerHTML = 'Shift: ' + form.Shift.value
        document.getElementById("print_Date").innerHTML = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
        document.getElementById("print_Time").innerHTML = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

        document.getElementById("print_AutoCaseCount").innerHTML = 'AutoCaseCount: ' + form.InsertQuantity.value

        csrf_token = document.getElementById("csrf_token").value
        jsonToServer = {
            'PalletNumber':PalletNumber
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
                        getbarcode(csrf_token,PalletNumber)
                        setTimeout(function(){print()}, 1000);
                        setTimeout(function(){document.getElementById("submit-button").click();}, 2000);
                    }

                });
              })
              .catch(function (error) {
                console.log("Fetch error: " + error);
              });

    }

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

                var html = '<hr><label for="InsertQuantity">Auto upload case count:</label><input name = "InsertQuantity" id ="InsertQuantity" value="'+ data.requiredCount + '" readonly></input><hr>';
                document.getElementById("ValidationPalletCounts").innerHTML = html;

            });
          })
          .catch(function (error) {
            console.log("Fetch error: " + error);
          });

}