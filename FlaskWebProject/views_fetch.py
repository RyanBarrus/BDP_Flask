from FlaskWebProject.globals import *
from flask import request, make_response, jsonify
from FlaskWebProject import app




@app.route("/fetch/palletcount", methods=["POST"])
def fetchPalletCount():
    req = request.get_json()
    query = "SELECT RequiredCount FROM [validation].[PalletCount] WHERE ItemNumber = ?"
    parameters = req['ItemNumber']
    requiredCount = bdp_sqlserver.get_rows(query, parameters)[0][0]

    query = "SELECT COUNT(*) AS PalletExistingCount FROM [data].[pallets] WHERE Pallet = ?"
    parameters = req['PalletNumber']
    PalletExistingCount = bdp_sqlserver.get_rows(query, parameters)[0][0]

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