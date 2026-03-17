// ============================================================
// ACMEMobility - Bank Service (Jolie)
// PORT 8000 : HTTP/REST  (used by Camunda Python workers)
// PORT 8080 : SOAP       (direct Camunda <-> Jolie communication)
//
// Operations:
//   preAuth             -> blocks 10€ on the card, returns a token
//   charge              -> charges the final amount (rental cost)
//   unlock              -> releases the caution (normal end of rental)
//   cancelAuthorization -> converts caution to charge (late cancellation / no-show)
// ============================================================

include "console.iol"
include "time.iol"

// ---- Types ----
type PreAuthorizeRequest: void {
    .cardId: string
    .amount: double
}
type PreAuthorizeResponse: void {
    .token: string
    .success: bool
    .message: string
}

type ChargeRequest: void {
    .token: string
    .finalAmount: double
}
type ChargeResponse: void {
    .success: bool
    .chargedAmount: double
    .message: string
}

type UnlockRequest: void {
    .token: string
}
type UnlockResponse: void {
    .success: bool
    .releasedAmount: double
    .message: string
}

type CancelAuthorizationRequest: void {
    .token: string
}
type CancelAuthorizationResponse: void {
    .success: bool
    .chargedAmount: double
    .message: string
}

// ---- Interface ----
interface BankInterface {
    RequestResponse:
        preAuth( PreAuthorizeRequest )( PreAuthorizeResponse ),
        charge( ChargeRequest )( ChargeResponse ),
        unlock( UnlockRequest )( UnlockResponse ),
        cancelAuthorization( CancelAuthorizationRequest )( CancelAuthorizationResponse )
}

// ---- REST/HTTP port on 8000 (for Camunda Python workers) ----
inputPort BankREST {
    Location: "socket://0.0.0.0:8000"
    Protocol: http {
        .format = "json";
        .method = "post"
    }
    Interfaces: BankInterface
}

// ---- SOAP port on 8080 (for direct Camunda <-> Jolie communication) ----
inputPort BankSOAP {
    Location: "socket://0.0.0.0:8080"
    Protocol: soap {
        .wsdl = "bank.wsdl";
        .wsdl.port = "BankPort"
    }
    Interfaces: BankInterface
}

// ---- Init ----
init {
    println@Console("=== Bank Service started ===")();
    println@Console("REST  -> port 8000  (/preAuth, /charge, /unlock, /cancelAuthorization)")();
    println@Console("SOAP  -> port 8080  (Camunda direct)")()
}

// ---- Main ----
main {

    // --- preAuth: blocks the caution on the card ---
    [ preAuth( req )( res ) {
        getCurrentTimeMillis@Time()( millis );
        token = "TOK-" + req.cardId + "-" + millis;

        global.authorizations.(token).cardId = req.cardId;
        global.authorizations.(token).amount = req.amount;
        global.authorizations.(token).status = "AUTHORIZED";

        res.token   = token;
        res.success = true;
        res.message = "Pre-authorization OK: EUR " + req.amount + " blocked for card " + req.cardId;

        println@Console("[BANK] preAuth -> " + token)()
    } ]

    // --- charge: charges only the final rental cost ---
    [ charge( req )( res ) {
        token = req.token;

        if ( is_defined( global.authorizations.(token) ) ) {
            if ( global.authorizations.(token).status == "AUTHORIZED" ) {
                global.authorizations.(token).chargedAmount = req.finalAmount;
                global.authorizations.(token).status = "CHARGED";

                res.success       = true;
                res.chargedAmount = req.finalAmount;
                res.message       = "Charged EUR " + req.finalAmount + " for token " + token
            } else {
                res.success       = false;
                res.chargedAmount = 0.0;
                res.message       = "Token already used (status: " + global.authorizations.(token).status + ")"
            }
        } else {
            res.success       = false;
            res.chargedAmount = 0.0;
            res.message       = "Token not found: " + token
        };

        println@Console("[BANK] charge -> " + token + " amount: " + req.finalAmount)()
    } ]

    // --- unlock: releases the caution (normal end of rental, after charge) ---
    [ unlock( req )( res ) {
        token = req.token;

        if ( is_defined( global.authorizations.(token) ) ) {
            if ( global.authorizations.(token).status == "CHARGED" ) {
                releasedAmount = global.authorizations.(token).amount;
                global.authorizations.(token).status = "RELEASED";

                res.success        = true;
                res.releasedAmount = releasedAmount;
                res.message        = "Caution of EUR " + releasedAmount + " released for token " + token
            } else {
                res.success        = false;
                res.releasedAmount = 0.0;
                res.message        = "Cannot release caution: status is " + global.authorizations.(token).status
            }
        } else {
            res.success        = false;
            res.releasedAmount = 0.0;
            res.message        = "Token not found: " + token
        };

        println@Console("[BANK] unlock (release caution) -> " + token)()
    } ]

    // --- cancelAuthorization: converts caution to charge (late cancellation / no-show) ---
    [ cancelAuthorization( req )( res ) {
        token = req.token;

        if ( is_defined( global.authorizations.(token) ) ) {
            if ( global.authorizations.(token).status == "AUTHORIZED" ) {
                cautionAmount = global.authorizations.(token).amount;
                global.authorizations.(token).status = "CANCELLED";

                res.success       = true;
                res.chargedAmount = cautionAmount;
                res.message       = "Caution of EUR " + cautionAmount + " converted to charge (late cancellation / no-show)"
            } else {
                res.success       = false;
                res.chargedAmount = 0.0;
                res.message       = "Cannot cancel: status is " + global.authorizations.(token).status
            }
        } else {
            res.success       = false;
            res.chargedAmount = 0.0;
            res.message       = "Token not found: " + token
        };

        println@Console("[BANK] cancelAuthorization -> " + token)()
    } ]
}
