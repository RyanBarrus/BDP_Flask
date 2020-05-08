
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
    var row_pallet = row + "_Pallet"
    var pallet = input.value
    var nextrow = Number(row) < 10 ? Number(row) + 1 : Number(row);
    var nextrow_pallet = nextrow + "_Pallet"

    csrf_token = document.getElementById("csrf_token").value
    jsonToServer = {
        "Pallet": pallet
    }

    if (pallet == "") {
        document.getElementsByName(row_pallet)[0].value = ""
        document.getElementsByName(row_itemnumber)[0].innerHTML = ""
        document.getElementsByName(row_quantity)[0].value = ""
    } else {
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

                        GPCounts = document.getElementsByName("GP Quantities")

                        var GPItems = []
                        for (var GPRow of GPCounts) {
                            var id = GPRow.id
                            var GPItemNumber = id.substr(id.indexOf('_') + 1)

                            GPItems.push(GPItemNumber)
                        }

                        var PalletItem = data.PalletDetails.ItemNumber

                        if (GPItems.indexOf(PalletItem) > 0) {
                            document.getElementsByName(row_itemnumber)[0].innerHTML = PalletItem
                            document.getElementsByName(row_quantity)[0].value = data.PalletDetails.Quantity
                            document.getElementsByName(nextrow_pallet)[0].focus()
                            reconcileremaining()
                        } else {
                            document.getElementsByName(row_pallet)[0].value = ""
                            document.getElementsByName(row_itemnumber)[0].innerHTML = ""
                            document.getElementsByName(row_pallet)[0].focus()
                            document.getElementsByName(row_quantity)[0].value = ""
                            toastr.error(pallet + " contains: " + PalletItem + " that item isn't used on the order");
                        }

                    } else {
                        document.getElementsByName(row_pallet)[0].value = ""
                        document.getElementsByName(row_itemnumber)[0].innerHTML = ""
                        document.getElementsByName(row_quantity)[0].value = ""
                        document.getElementsByName(row_pallet)[0].focus()
                        toastr.error(pallet + " doesn't have any cases assigned to it");
                    }

                });
              })
              .catch(function (error) {
                console.log("Fetch error: " + error);
              });
    }
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
                    html += '<td name="GP Quantities" id= "GP_' + data.OrderDetails[i]['ItemNumber'] + '">' + data.OrderDetails[i]['GPQuantity'] + "</td>";
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

function reconcileremaining() {

    table = document.getElementById("PalletHolders")

    var InputCounts = {}
    for (let row of table.rows)
    {
        var RowItem = ""
        var RowQty
        for(let cell of row.cells)
        {

            if (cell.className == "ItemNumbersJS") {
                RowItem = cell.innerHTML
            }

            if (cell.childNodes.length > 0) {
                if (cell.childNodes[0].className == "QuantitiesJS") {
                    RowQty = cell.childNodes[0].value
                }
            }

        }
        if (RowItem != "") {
            if (RowItem in InputCounts) {
                InputCounts[RowItem] += Number(RowQty)
            } else {
                InputCounts[RowItem] = Number(RowQty)
            }
        }

    }

    GPCounts = document.getElementsByName("GP Quantities")

    var GPItemCounts = {}
    for (var GPRow of GPCounts) {
        var id = GPRow.id
        var GPItemNumber = id.substr(id.indexOf('_') + 1)
        var GPQuantity = Number(GPRow.innerHTML)
        GPItemCounts[GPItemNumber] = GPQuantity
    }

    for (InputItemNumber in InputCounts) {
        if (InputItemNumber in GPItemCounts) {
            GPItemCounts[InputItemNumber] -= InputCounts[InputItemNumber]
        }
    }

    var GPRemaining = document.getElementsByName("Remaining Quantities")

    for (var GPRem of GPRemaining) {
        GPRem.innerHTML = GPItemCounts[GPRem.id]
    }

}