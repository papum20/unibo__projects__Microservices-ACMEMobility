# Formal Choreography

## Formal syntax definition

Let the participants be:
* **U** User
* **A** ACMEMobility
* **B** Bank
* **F** (Fleet Management)
* **S** (Station)
* **V** (Vehicle)

The choreography $C$ is defined as the choice between an Immediate Rental ($C_{imm}$) and a Reservation ($C_{res}$):

$C = C_{imm} + C_{res}$

**Immediate Rental:**  
$C_{imm} =$  
$\ \ \ \ req\_imm: U \rightarrow A ;$  
$\ \ \ \ caut\_lock: A \rightarrow B ; ( $  
$\ \ \ \ \ \ \ \ caut\_lock\_err: B \rightarrow A ; C_{err\_reject} + $  
$\ \ \ \ \ \ \ \ caut\_locked: B \rightarrow A ; notify\_imm: A \rightarrow U ; C_{ride\_start} $  
$\ \ \ \ )$ 

**Reservation:**  
$C_{res} =$  
$\ \ \ \ req\_res: U \rightarrow A ;$  
$\ \ \ \ caut\_lock: A \rightarrow B ; ( $  
$\ \ \ \ \ \ \ \ caut\_lock\_err: B \rightarrow A ; C_{err\_reject} + $  
$\ \ \ \ \ \ \ \ caut\_locked: B \rightarrow A ; reserved: A \rightarrow U ; ( C_{cancel} + C_{scan\_res} ) $  
$\ \ \ \ )$ 

// each request to the bank may return an ok or an error (in which case we go to err_manual)  
$C_{cancel} = $  
$\ \ \ \ cancel: U \rightarrow A ; ( $  
$\ \ \ \ \ \ \ \ \ caut\_release: A \rightarrow B ; ( caut\_release\_err: B \rightarrow A ; C_{err\_manual} + caut\_released: B \rightarrow A) + $  
$\ \ \ \ \ \ \ \ \ charge\_pen: A \rightarrow B; (charge\_pen\_err: B \rightarrow A ; C_{err\_manual} + charged\_pen: B \rightarrow A) $  
$\ \ \ \ )$

$C_{scan\_res} = scan\_res: U \rightarrow A ; C_{ride\_start} $  

**Ride, Start and End of rental:**  
// even the vehicle could return success or error: for simplicity, here we show as if only Fleet can cause and return error  
$C_{ride\_start} = $  
$\ \ \ \ track\_start: A \rightarrow F ; share\_start: F \rightarrow V ; share\_started: V \rightarrow F ; ( $  
$\ \ \ \ \ \ \ \ track\_err: F \rightarrow A; C_{err\_release} +$  
$\ \ \ \ \ \ \ \ track\_started: F \rightarrow A ; unlock: A \rightarrow S ; $  
$\ \ \ \ \ \ \ \ ( unlock\_err: S \rightarrow A ; C_{err\_release} + unlock\_ok: S \rightarrow A ; unlocked: A \rightarrow U ; C_{ride} )$  
$\ \ \ \ )$

// We omit here the loop where Fleet periodically receives the information (position and battery) from the vehicle, which is a separate loop, i.e. the information is then cached, so it can happen asynchronously with ACME and in parallel.  
// Explicitly adding these details (for vehicles) would just make the formula more complex, since the mechanisms of both errors and loop are analogous to the ones involving Fleet.  
// A failed parking/locking attempt may happen 0 or more times, until either success or assistance request.  
$C_{ride} =$   
$\ \ \ \ (pos\_fetch: A \rightarrow F ; pos\_fetched: F \rightarrow A )* ; $  
$\ \ \ \ C_{park\_attempt}* ; ( $  
$\ \ \ \ \ \ \ \ C_{park\_attempt} ; assist: U \rightarrow A + $  
$\ \ \ \ \ \ \ \ park: U \rightarrow A ; lock: A \rightarrow S ; lock\_ok: S \rightarrow A ; C_{ride\_end} $  
$\ \ \ \ )$

$C_{park\_attempt} = ( park: U \rightarrow A ; lock: A \rightarrow S ; lock\_err: S \rightarrow A ; park\_err: A \rightarrow U ) $
  
// Each request to the bank may return an ok or an error (in which case we go to err_manual).  
// If the track_stop request fails (err_track_stop), we go on but will later ask for manual intervention.  
// In this part, in case of an error, we notify the user in most cases, since he's expecting either a confirmation of the ride's end or aa message of error, in the choreography.  
$C_{ride\_end} =$  
$\ \ \ \ ask\_batt: A \rightarrow F ; ( $  
$\ \ \ \ \ \ \ \ (err\_share\_batt: F \rightarrow A; C_{err\_manual\_notify}) + $  
$\ \ \ \ \ \ \ \ share\_batt: F \rightarrow A ; $  
$\ \ \ \ \ \ \ \ track\_stop: A \rightarrow F ; share\_stop: F \rightarrow V , share\_stopped: V \rightarrow F ; ( track\_stopped: F \rightarrow A + (err\_track\_stopped: F \rightarrow A; C_{err\_manual})) ; $  
$\ \ \ \ \ \ \ \ charge: A \rightarrow B ; ( $  
$\ \ \ \ \ \ \ \ \ \ \ \ charge\_err: B \rightarrow A ; C_{err\_manual\_notify} + $  
$\ \ \ \ \ \ \ \ \ \ \ \ charged: B \rightarrow A ; receipt: A \rightarrow U ; caut\_release: A \rightarrow B ; ($  
$\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ caut\_release\_err: B \rightarrow A ; C_{err\_manual} + $  
$\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ caut\_released: B \rightarrow A $  
$\ \ \ \ \ \ \ \ \ \ \ \ )$  
$\ \ \ \ \ \ \ \ ))$

**Errors:**

// manual intervention  
$C_{err\_manual} = 1$

// manual intervention, notifying the user  
$C_{err\_manual\_notify} = notify\_err\_manual: A \rightarrow U $

// can't start the ride, so unlock the caution and notify user, or require manual intervention in case of bank error even here  
$C_{err\_release} = $  
$\ \ \ \ caut\_release: A \rightarrow B ; ( $  
$\ \ \ \ \ \ \ \ C_{err\_manual} + caut\_released: B \rightarrow A ; C_{err\_reject} $  
$\ \ \ \ )$

// reject rental in the first place, without even involving the bank  
$C_{err\_reject} = notify\_reject: A \rightarrow U $  

### Notes

Ack responses, while could be omitted for simplicity, are fundamental for connectednes, so that the first sender can know when to act again.  
All error cases (error responses or unreachable/network errors) follow the same pattern.  

#### Connectedness Analysis

A choreography is "connected" if the sequences of interactions guarantee causality safety (i.e., a participant knows when to act without central control).  
In our choreography, looking at any sequence $o: a \rightarrow b ; o': c \rightarrow d$, the connectedness condition ($a=c \lor a=d \lor b=c \lor b=d$) is **always satisfied**.   
This is because **ACMEMobility (A)** acts as the central orchestrator. Every single interaction involves participant $A$, which is usually the one making requests and then waiting for answers. This creates a "Star Topology" centered on $A$. Since $A$ is present in every step, causality is safe, and there are no communication deadlocks or race conditions (in fact, this satisfies the synchronous case connectedness condition `a=c or a=d or b=c or b=d`).  
The only exception is User, which is the first initiator itself, usually making the first requests to ACME: in most cases, we've had to add confirmation messages from ACME to grant connectedness, otherwise User couldn't have known when to speak again, after having already sent a message.  
Every time we're using the 1 (skip) instruction, either the choreography ends there with a choice (+) (so there's no other following interaction hanging) or we use the parallel instruction (|) (which, again, in one branch ends, while in the other goes on and preserves the causal relationships), so we're always returning something and who made a request always knows it's again his turn to act.  
The projection will perfectly conform to the choreography.  

#### Projection
Projections show how the global formula translates into local code for the endpoints.  
All interactions are synchronous: the choreography has no parallel branches. In the BPMN, the only parallel branches bring as second path to the manual intervention (unlinked to other services) - besides the first, main path.  
1s mean errors (i.e. err_manual, which terminates the choreography process, without needing further interactions).  
Note: we use a `1` as a placeholder, to indicate some actions which wouldn't be codified in this projection, since they don't involve a communication between participants - e.g. manual errors, meaning that something will happen in that place.  
Note: for some participants, the whole choreography or a suffix of it may not happen, in case of errors happen in the mean time.  


**Projection on roles:**  
Applying the projection operator $proj(C, p)$, we obtain the local behavior of each role.

*Projection for Bank (B)*  
$proj(C_{imm}, B) = caut\_lock@A ; (\overline{caut\_lock\_err}@A + \overline{caut\_locked}@A ; proj(C_{ride\_start}, B) ) $

$proj(C_{res}, B) = caut\_lock@A ; (\overline{caut\_lock\_err}@A + \overline{caut\_locked}@A ; (proj(C_{cancel}, B) + proj(C_{ride\_start}, B)) ) $

$proj(C_{cancel}, B) = $  
$\ \ \ \ caut\_release@A ; $  
$\ \ \ \ ((\overline{caut\_release\_err}@A + \overline{caut\_released}@A) + charge\_pen@A ; (\overline{charge\_pen\_err}@A + \overline{charged\_pen}@A) ) $

$proj(C_{ride\_start}, B) = caut\_release@A ; ( \overline{caut\_release\_err}@A + \overline{caut\_released}@A ; proj(C_{ride\_end}, B) ) $  

$proj(C_{ride\_end}, B) = $  
$\ \ \ \ charge@A ; $  
$\ \ \ \ ( \overline{charge\_err}@A + ( \overline{charged}@A ; caut\_release@A ; ( \overline{caut\_release\_err}@A + \overline{caut\_released}@A ) ) ) $ 

*Projection for Fleet Management (F)*  
$proj(C, F) = ( $  
$\ \ \ \ 1 + $  
$\ \ \ \ track\_start@A ; share\_start@V ; \overline{share\_started}@V ; (\overline{track\_err}@A + \overline{track\_started}@A ; proj(C_{ride}, F) )$  
$ ) $

$proj(C_{ride}, F) = (pos\_fetch@A ; \overline{pos\_fetched}@A )* ; proj(C_{ride\_end}, F) $

$proj(C_{ride\_end}, F) = $  
$\ \ \ \ ask\_batt@A ; ( $  
$\ \ \ \ \ \ \ \ \overline{err\_share\_batt}@A + $  
$\ \ \ \ \ \ \ \ \overline{share\_batt}@A ; track\_stop@A ; \overline{share\_stop}@V ;share\_stopped@V ; (\overline{err\_track\_stopped}@A + \overline{track\_stopped}@A ) $  
$\ \ \ \ ) $  

*Projection for ACMEMobility (A)*  
$proj(C_{imm}, A) = req\_imm@U ; \overline{caut\_lock}@B ; $  
$\ \ \ \ ( caut\_lock\_err@B ; \overline{notify\_reject}@U + caut\_locked@B ; proj(C_{ride\_start}, A) ) $

$proj(C_{res}, A) = req\_res@U ; \overline{caut\_lock}@B ; $  
$\ \ \ \ ( caut\_lock\_err@B ; \overline{notify\_reject}@U + caut\_locked@B ; \overline{notify\_reserved}@U ; (proj(C_{cancel}, A) + proj(C_{scan\_res}, A)) ) $

$proj(C_{cancel}, A) = $  
$\ \ \ \ cancel@U ; ( $  
$\ \ \ \ \ \ \ \ \overline{caut\_release}@B ; (caut\_release\_err@B + caut\_released@B) + $  
$\ \ \ \ \ \ \ \ \overline{charge\_pen}@B ; (charge\_pen\_err@B + charged\_pen@B) $  
$\ \ \ \ )$

$proj(C_{scan\_res}, A) = scan\_res@U ; proj(C_{ride\_start}, A) $

$proj(C_{ride\_start}, A) = $  
$\ \ \ \ \overline{track\_start}@F ; ( track\_err@F ; proj(C_{err\_release}, A) + $  
$\ \ \ \ \ \ \ \ track\_started@F ; \overline{unlock}@S ; ( unlock\_err@S ; proj(C_{err\_release}, A) + unlock\_ok@S ; \overline{unlocked}@U ; proj(C_{ride}, A) ) $  
$\ \ \ \ ) $

$proj(C_{ride}, A) = $  
$\ \ \ \ (\overline{pos\_fetch}@F ; pos\_fetched@F )* ; proj(C_{park\_attempt}*, A) ; $  
$\ \ \ \ ( proj(C_{park\_attempt}, A) ; assist@U + park@U ; \overline{lock}@S ; lock\_ok@S ; proj(C_{ride\_end}, A) ) $

$proj(C_{park\_attempt}, A) = park@U ; \overline{lock}@S ; lock\_err@S ; \overline{park\_err}@U $

$proj(C_{ride\_end}, A) = $  
$\ \ \ \ \overline{ask\_batt}@F ; ( $  
$\ \ \ \ \ \ \ \ err\_share\_batt@F ; \overline{notify\_err\_manual}@U + $  
$\ \ \ \ \ \ \ \ \overline{share\_batt}@F ; \overline{track\_stop}@F ; ((err\_track\_stopped@F | 1) + track\_stopped@F) ; $  
$\ \ \ \ \ \ \ \ \overline{charge}@B ; ( $  
$\ \ \ \ \ \ \ \ \ \ \ \ charge\_err@B ; \overline{notify\_err\_manual}@U + $  
$\ \ \ \ \ \ \ \ \ \ \ \ charged@B ; \overline{receipt}@U ; \overline{caut\_release}@B ; ((caut\_release\_err@B ; 1) + caut\_released@B) $  
$\ \ \ \ \ \ \ \ ) $  
$\ \ \ \ ) $

$proj(C_{err\_release}, A) = $  
$\ \ \ \ \overline{caut\_release}@B ; $  
$\ \ \ \ (caut\_release\_err@B ; 1 + caut\_released@B) ; \overline{notify\_reject}@U $

*Projection for Station (S)*  
// station projection only includes the unlock and the lock loop  
$proj(C, S) = ( $  
$\ \ \ \ 1 + $  
$\ \ \ \ unlock@A ; ( $  
$\ \ \ \ \ \ \ \ \overline{unlock\_err}@A + $  
$\ \ \ \ \ \ \ \ \overline{unlock\_ok}@A ; $  
$\ \ \ \ \ \ \ \ ( lock@A ; \overline{lock\_err}@A )* ; ( lock@A ; \overline{lock\_ok}@A | 1 ) $  
$\ \ \ \ ) $
$ ) $

*Projection for User (U)*  
$proj(C_{imm}, U) = \overline{req\_imm}@A ; proj(C_{scan}, U) $  

$proj(C_{res}, U) = $  
$\ \ \ \ \overline{req\_res}@A ; ( $  
$\ \ \ \ \ \ \ \ notify\_reject@A + $  
$\ \ \ \ \ \ \ \ notify\_reserved@A ; (\overline{cancel}@A + \overline{scan}@A ; proj(C_{scan}, U)) $  
$\ \ \ \ )$

// Scan is valid both for immediate scan or scan after reservation (so we don't have to repeat this)  
$proj(C_{scan}, U) = notify\_reject@A + unlocked@A ; proj(C_{ride}, U) $  

$proj(C_{ride}, U) = $  
$\ \ \ \ (\overline{park}@A ; park\_err@A )* ; \overline{park}@A ; ( $  
$\ \ \ \ \ \ \ \ park\_err@A ; \overline{assist}@A + $  
$\ \ \ \ \ \ \ \ park\_ok@A ; (notify\_err\_manual@A + receipt@A) $  
$\ \ \ \ )$

*Projection for Vehicle (V)*  
// Again, we omit errors and loop for Vehicle.  

$proj(C, V) = ( $  
$\ \ \ \ 1 + $  
$\ \ \ \ share\_start@F ; \overline{share\_started}@F ; $  
$\ \ \ \ ( 1 + share\_stop@F ; \overline{share\_stopped}@F ) $  
$ ) $

// An example of Fleet-Vehicle interaction loop would be:  
$proj(C_{ride_loop}, V) = ( pos\_fetch@F ; \overline{pos\_fetched}@F )* $


*(Note on syntax: The overline $\overline{o}$ means "sending a message", and no overline means "receiving a message").*

