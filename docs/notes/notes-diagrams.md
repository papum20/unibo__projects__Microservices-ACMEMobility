pre-auth token: identifies the session started with the caution money deposit
* avoids saving credit card info
* can be used for multiple transactions (block, charge, then release the caution money)

implementation:
* everything with external tasks for consistency, manageability, debugging
* timers: some may be lower, for the sake of testing and presentation
* errors:
  * fetch vehicle battery (at the end): for simplicity and not to make user wait, if we couldn't fetch it we will charge him without penalty (and assume manual checks and maintenance will be performed later)