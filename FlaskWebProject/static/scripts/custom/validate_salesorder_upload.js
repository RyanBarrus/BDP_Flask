
function validate(form) {
    event.preventDefault();

    var PalletHolders = document.getElementsByClassName("PalletsJS")
    var Pallets = new Array();
    for (PalletHolder of PalletHolders) {
        if (PalletHolder.value != "") {
            Pallets.push(PalletHolder.value)
        }
    }
    var PalletCount = Pallets.length
    var uniques = new Set(Pallets)

    var remainings = document.getElementsByName("Remaining Quantities")

    QuantitiesOk = 1
    for (var remaining of remainings) {
        if (remaining != "0") {
            QuantitiesOk = 0

            break;
        }
    }

    if (uniques.size != PalletCount) {
        toastr.error("A pallet is used more than once, please review");
    } else if (QuantitiesOk == 0) {
        toastr.error("All remaining quantities must be 0")
    } else {
        //form.submit()
    }

}


function getpalletdetails(input) {
    var inputname = input.name
    var row = inputname.substr(0, inputname.indexOf('_'));
    var row_itemnumber = row + "_ItemNumber"
    var row_quantity = row + "_Quantity"
    var pallet = input.value
    var nextrow = Number(row) < 10 ? Number(row) + 1 : Number(row);
    var nextrow_pallet = nextrow + "_Pallet"

    csrf_token = document.getElementById("csrf_token").value
    jsonToServer = {
        "Pallet": pallet
    }

    fetch(`${window.origin}/fetch/palletdetails`, {
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

                if(data["UsedPallet"] != "") {
                    toastr.error("This pallet is already assigned to Sales Order: " + data["UsedPallet"]);
                    input.value = ""
                } else if ("PalletDetails" in data) {
                    document.getElementsByName(row_itemnumber)[0].innerHTML = data.PalletDetails.ItemNumber
                    document.getElementsByName(row_quantity)[0].value = data.PalletDetails.Quantity
                    document.getElementsByName(nextrow_pallet)[0].focus()

                    MatchingGPVal = document.getElementById(data.PalletDetails.ItemNumber)

                    if (MatchingGPVal) {
                        old = Number(MatchingGPVal.innerHTML)
                        MatchingGPVal.innerHTML = old - data.PalletDetails.Quantity
                    }
                }






            });
          })
          .catch(function (error) {
            console.log("Fetch error: " + error);
          });

}


window.onload = getorderdetails;
function getorderdetails() {
    var selected = document.getElementById("Available").value;
    csrf_token = document.getElementById("csrf_token").value
    jsonToServer = {
        'SONumber':selected
    }


    fetch(`${window.origin}/fetch/orderdetails`, {
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

                var html = '<hr><table border="1"><tr><th>ItemNumber</th><th>GP Quantity</th><th>Remaining Quantity</th></tr><tr>';

                for (var i=0; i<data.OrderDetails.length; i++) {
                    html += "<td >" + data.OrderDetails[i]['ItemNumber'] + "</td>";
                    html += "<td>" + data.OrderDetails[i]['GPQuantity'] + "</td>";
                    html += '<td name="Remaining Quantities" id= "' + data.OrderDetails[i]['ItemNumber'] + '">' + data.OrderDetails[i]['Remaining'] + "</td>";

                    if (i+1!=data.OrderDetails.length) {
                      html += "</tr><tr>";
                    }
                }
                html += "</tr></table><hr>";

                document.getElementById("OrderDetails").innerHTML = html;
            });
          })
          .catch(function (error) {
            console.log("Fetch error: " + error);
          });

}