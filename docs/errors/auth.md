Auth Invalid
-------------

This is one of the most common errors experienced with 1P - it's a general error that can be troublesome to track down.

With `auth invalid`, you will receive a response from the server similar to `[{"id":0,"status":"invalid"}]`. This means that something in the 'calls' portion of your command is incorrect.

It's not related to anything authentication related - it's strictly something with the arguments portion of the RPC command.

` { auth: {cik:''}, calls:[ {alias:"", arguments: {limit:1}}]} `

Common things to check:
* You are using a CIK
* Your CIK is valid
* Your CIK is activated

