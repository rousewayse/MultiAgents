#!/bin/bash

XMPP_server="127.0.0.1"
JID_prefix="agent"
fake_pass="mypass"
for i in {0..20} 
do
	sudo prosodyctl register $JID_prefix$i $XMPP_server $fake_pass
done
