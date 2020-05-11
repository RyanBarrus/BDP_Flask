function getbarcode(csrf_token, PalletNumber) {
    jsonToServer = {
        'ToBarcode':PalletNumber
    }

    fetch(`${window.origin}/fetch/barcode`, {
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
                barcodeimage = document.getElementById("barcodeimage")
                bytestring = data['barcodeimage']
			    image = bytestring.split('\'')[1]
				barcodeimage.src = 'data:image/jpeg;base64,'+image
            });
          })
          .catch(function (error) {
            console.log("Fetch error: " + error);
          });
}