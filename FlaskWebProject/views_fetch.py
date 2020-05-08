from FlaskWebProject.globals import *
from flask import request, make_response, jsonify
from FlaskWebProject import app



def lookupPalletCount(ItemNumber):
    query = "SELECT RequiredCount FROM [validation].[PalletCount] WHERE ItemNumber = ?"
    parameters = ItemNumber
    requiredCount = bdp_sqlserver.get_rows(query, parameters)[0][0]
    return(requiredCount)


def lookupPalletExisting(ItemNumber):
    query = "SELECT COUNT(*) AS PalletExistingCount FROM [data].[pallets] WHERE Pallet = ?"
    parameters = ItemNumber
    PalletExistingCount = bdp_sqlserver.get_rows(query, parameters)[0][0]
    return(PalletExistingCount)





@app.route("/fetch/lookuppalletcount", methods=["POST"])
def fetchLookupPalletCount():
    req = request.get_json()
    requiredCount = lookupPalletCount(req['ItemNumber'])

    return make_response(jsonify({"requiredCount": requiredCount}), 200)


@app.route("/fetch/lookuppalletexisting", methods=["POST"])
def fetchLookupPalletExisting():
    req = request.get_json()
    PalletExistingCount = lookupPalletCount(req['ItemNumber'])

    return make_response(jsonify({"PalletExistingCount": PalletExistingCount}), 200)


@app.route("/fetch/validatepallet", methods=["POST"])
def fetchValidatePallet():
    req = request.get_json()
    ItemNumber = req['ItemNumber']
    requiredCount = lookupPalletCount(ItemNumber)
    PalletExistingCount = lookupPalletExisting(ItemNumber)

    ExistingPalletAssignment = {}
    if 'CaseCodes' in req:
        CaseCodes = ','.join(req['CaseCodes'])
        query = "EXEC validation.CheckExistingCaseBarcodes @CasesString = ?"
        parameters = CaseCodes
        FoundPalletAssignment = bdp_sqlserver.get_rows(query,parameters)

        if len(FoundPalletAssignment) > 0:
            ExistingPalletAssignment = {
                        "Pallet": FoundPalletAssignment[0][0],
                        "CaseBarcode": FoundPalletAssignment[0][1]
                }

    return make_response(jsonify({"requiredCount": requiredCount,
                                  "PalletExistingCount": PalletExistingCount,
                                  "ExistingPalletAssignment": ExistingPalletAssignment}), 200)


@app.route("/fetch/orderdetails", methods=["POST"])
def fetchOrderDetails():
    req = request.get_json()
    query = "SELECT * FROM dbo.SOP10200 WHERE SOPNUMBE = ? UNION SELECT *  FROM dbo.SOP30300 WHERE SOPNUMBE = ?"
    SONumber = req['SONumber']
    parameters = (SONumber,SONumber)
    expecteds = bhprd_sqlserver.get_rows(query, parameters)

    OrderDetails = [{"ItemNumber": x[1], "GPQuantity": x[2], "Remaining": x[2]} for x in expecteds]

    return make_response(jsonify({"OrderDetails": OrderDetails}), 200)

@app.route("/fetch/palletdetails", methods=["POST"])
def fetchPalletDetails():
    req = request.get_json()
    Pallet = req['Pallet']
    query = "SELECT TOP 1 SalesOrderNumber FROM data.shipments WHERE Pallet = ?"
    parameters = (Pallet)
    UsedRecords = bdp_sqlserver.get_rows(query, parameters)
    UsedPallet = "" if len(UsedRecords) == 0 else UsedRecords[0][0]


    query = "SELECT ItemNumber, COUNT(*) FROM data.pallets WHERE pallet = ? GROUP BY ItemNumber"
    parameters = (Pallet)
    PalletRecords = bdp_sqlserver.get_rows(query, parameters)

    if len(PalletRecords) > 0:
        PalletItemQuantity = PalletRecords[0]
        PalletDetails = {"ItemNumber": PalletItemQuantity[0],"Quantity": PalletItemQuantity[1]}
        return make_response(jsonify({"PalletDetails": PalletDetails,
                                      "UsedPallet": UsedPallet}), 200)
    else:
        return make_response(jsonify({"UsedPallet": UsedPallet}), 200)



