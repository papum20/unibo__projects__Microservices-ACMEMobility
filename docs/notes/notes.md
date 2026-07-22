## ACME

ACME keeps track of some information (see `acme-db.md`)
* storing them (eg vehicle current station) here is the best choice:
  * asking to user isnt good
  * checking coordinates may be imprecise
  * in general, for separation of concerns, other services shouldnt be responsible this
* DB:
  * each service (inlcuding ACME) may have its own DB, accessible only by itself
  * in the implementation, we just simulated it (e.g. with a python module inside the same Docker container)

locking:
* user side communicates `stationId` when parking:
  * this is the most reliable way (GPS unreliable and no other service could provide this information)
  * in real life, it would be some one-time code provided by the station
  * ACME still needs to verify the lock is successful with the Stations service; otherwise, it will ask for manual intervention

locking assistance request:
* user can ask for assistance if they have trouble locking the vehicle at the end of the ride
  * ACME proceeds to ending the ride and charging the user
  * at the same time, an operator has been informed and will go physically as soon as possible
  * we assume that the vehicle can only be ridden by the user who rented it, or that, anyway, there is some auto-lock mechanism for the vehicle, so it can be leaved unwatched without risk of theft and the user doesn't have to wait there

## Bank

* `execution { concurrent }`:
  * provides an infinite loop (keep the service running for following operations)
  * can serve multiple users at the same time

## Fleet

* BPMN:
  * The fetch loop actually happens separately, at the same time, for both battery and position

## User
By user we mean both the person and his device/app (so, including some information the user doesn't directly know, but the app provides, like codes or ids of vehicles).  

reserve/scan:
* we assume that the user can only pick an available vehicle - the app simply won't show the other ones


### Report

Errors to report:
* notes on connectedness in formal
* correctedness
* show error in diagram-error.bpmn

#### UML

We combine Class Diagram syntax (defining methods inside an interface using { ... }) with Component Diagram syntax (component, portout, and package).  

Following the SOMA (Service-Oriented Modeling and Architecture) methodology, we extracted our Service Architecture directly from the BPMN Collaboration diagram.  
According to SOMA, each external Pool in the BPMN (`Bank`, `Fleet Management`, `Stations`) represents a **Capability** modeled as an **Entity Service** (`<<Entities>>`). The incoming Message Flows to those pools (e.g., 'request to lock vehicle', 'request to block caution') dictate the exact operations exposed by their **Service Interfaces** (`<<ServiceInterface>>`).  
The central BPMN executable pool (`ACMEMobility`) is modeled as a **Task Service** (`<<Tasks>>`), which encapsulates the business process. Through the Camunda External Task pattern (represented by the `<<use>>` dependencies in UML), the Task Service acts as an orchestrator, invoking the Entity Services via SOAP and REST to fulfill the business capabilities.


`<<Entities>>` represent IT Software Services that manage business domains (so, no User nor Vehicle).  
*   **The User** is a human interacting with a client (Mobile App). The app is a *Consumer* of your SOA, not a service within it.
*   **The Vehicle** is physical IoT hardware. The **Fleet Management Service** is already the "Digital Twin" (the software representation) of the vehicles. 

Instead of making them SOA Entities, we add them to the UML diagram as **External Actors** to show how they interact with the system boundaries.


Stations are multiple identical instances of the same microservice: draw **one** component box, but visually indicate that it is a "class" or "template" that is instantiated multiple times.  


##### Specifications of UML/TinySOA

TinySOA organizes services into specific packages (layers):
*   **`<<Tasks>>` (Business Process Services):** These orchestrate the workflow. **ACMEMobility** belongs here.
*   **`<<Entities>>` (Entity Services):** These manage specific domain data/hardware and are reusable. **Bank, Fleet, and Stations** belong here.
*   *(Utilities are generic things like logging/email, which you don't need to model).*
*   **`<<Capability>>`**: This is the "concept" of what the service does (e.g., "Payment Management", "Docking Management"). **In SOMA, every Pool in BPMN becomes a Capability.**
*   **`<<ServiceInterface>>`**: This is the actual API (the endpoints) exposed by the microservice. **In SOMA, the incoming arrows (Message Flows) to a Pool become the Operations in the Interface.**

#### Choreography
A choreography is a model where there is no central controller; every service just knows its own part.

#### Connectedness
A **theoretical property** of Service Choreographies: a choreography is "connected" if every participant knows exactly when it is their turn to speak, based *only* on the messages they have already sent or received.  
in other words: A choreography is "connected" if, for every sequence of actions, the person who is supposed to send a message **knows** that it is their turn because they were the **receiver** of the previous message.  

**Example of a DISCONNECTED (Bad) Choreography:**
1.  **Customer** sends "Start Rental" to **ACMEMobility**.
2.  **Bank** sends "Payment Confirmed" to **ACMEMobility**.

bad: The **Bank** doesn't know when step 1 happened (wasn't involved at all)! There is no message between the Customer and the Bank, or ACMEMobility and the Bank yet. The Bank is "speaking" out of nowhere. 

**Example of a CONNECTED (Good) Choreography:**
1.  **Customer** sends "Start Rental" to **ACMEMobility**.
2.  **ACMEMobility** sends "Request Pre-auth" to **Bank**.
3.  **Bank** sends "Auth Token" to **ACMEMobility**.

good: Every step follows a logical flow. The Bank only speaks *after* it receives a message from ACMEMobility. There is a causal link (ACME is receiver of 1 and sender of 2, bank is receiver of 2 and sender of 3). The "baton" is passed correctly.  

"need to draw the interaction".  
If you see a service performing an action without having received a message that "triggered" that action, the choreography is **not connected**, you will have to "refine" it by adding the missing messages.

##### Correctness (or Correctedness)
much broader term. It usually refers to **Realizability** and **Semantic Correctness**.  

*   **Realizability:** Can this choreography actually be implemented as a set of microservices without them getting stuck (deadlock)? If your choreography is *Connected*, it is a huge step toward being *Realizable*.
*   **Liveness:** Does the process always reach the end? (e.g., the car is always eventually locked and paid for).
*   **Safety:** Does the process avoid "bad" states? (e.g., the car is unlocked but the bank never authorized the payment).
