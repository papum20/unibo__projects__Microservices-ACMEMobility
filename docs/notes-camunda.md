## Time
TTL: `P10D` (10 days)  
timer: `PT5M` (5 minutes)  

## Script
JUEL (Java Unified Expression Language)  
```
${variable}
${expression}
```

## Connector Input
Content-Type:
* Nella mappa headers, la chiave Content-Type deve avere valore text/xml (oppure application/soap+xml se usi SOAP 1.2, ma text/xml è lo standard più comune per SOAP 1.1).
* rest: application/json
Method: È sempre POST. SOAP viaggia via HTTP POST.
URL: È l'indirizzo del tuo container Jolie (es. http://bank-service:8000/BankPort).
Payload: Qui incollerai l'XML completo (<soapenv:Envelope>...).

## Forms
Simulate human interaction.  
Alternative: input values manually at BPMN start.  

## Calls
**`businessKey`**: Used by Camunda to index process instances (e.g. to this specific vehicle)