

# Bank Service API Reference

The Bank Service is implemented in Jolie and exposes the same business logic through two different interfaces to support diverse integrations: a **REST/JSON** interface for standard web clients, and a **SOAP/XML** interface for enterprise orchestrators (BPMS).

### Base URLs
*   **REST (JSON):** `http://<bank-service-host>:8000`
*   **SOAP (XML):** `http://<bank-service-host>:8080`

---

## 1. Pre-Authorization (`preAuth`)
Blocks a specified amount on the user's card as a caution/deposit. Returns a unique transaction token.

*   **REST Endpoint:** `POST /preAuth`
*   **SOAP Operation:** `<preAuth>`

**REST Request (JSON):**
```json
{
  "cardId": "USER-CARD-1234",
  "amount": 10.0
}
```

**SOAP Request (XML):**
```xml
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Body>
        <preAuth>
            <cardId>USER-CARD-1234</cardId>
            <amount>10.0</amount>
        </preAuth>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
```

**Response (REST & SOAP representation):**
*   `token` *(string)*: Unique identifier for the authorization (e.g., `TOK-USER-CARD-1234-1711468000000`)
*   `success` *(boolean)*: `true` if the funds were successfully blocked.
*   `message` *(string)*: Human-readable status message.

---

## 2. Charge (`charge`)
Captures the final rental cost from the previously blocked caution.

*   **REST Endpoint:** `POST /charge`
*   **SOAP Operation:** `<charge>`

**REST Request (JSON):**
```json
{
  "token": "TOK-USER-CARD-1234-1711468000000",
  "finalAmount": 7.50
}
```

**Response Properties:**
*   `success` *(boolean)*: `true` if the charge was successful.
*   `chargedAmount` *(double)*: The actual amount captured.
*   `message` *(string)*: Status message.

---

## 3. Unlock Caution (`unlock`)
Releases the remaining uncharged funds from the pre-authorization block. Used at the normal end of a rental after the charge is complete.

*   **REST Endpoint:** `POST /unlock`
*   **SOAP Operation:** `<unlock>`

**REST Request (JSON):**
```json
{
  "token": "TOK-USER-CARD-1234-1711468000000"
}
```

**Response Properties:**
*   `success` *(boolean)*: `true` if the release was successful.
*   `releasedAmount` *(double)*: The amount released back to the user's available balance.
*   `message` *(string)*: Status message.

---

## 4. Cancel Authorization (`cancelAuthorization`)
Converts the entire pre-authorized caution into a charge. Used when a user incurs a penalty (e.g., late cancellation or no-show).

*   **REST Endpoint:** `POST /cancelAuthorization`
*   **SOAP Operation:** `<cancelAuthorization>`

**REST Request (JSON):**
```json
{
  "token": "TOK-USER-CARD-1234-1711468000000"
}
```

**Response Properties:**
*   `success` *(boolean)*: `true` if the conversion was successful.
*   `chargedAmount` *(double)*: The penalty amount captured (equals the original caution).
*   `message` *(string)*: Status message.

***