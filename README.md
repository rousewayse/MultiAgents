# MultiAgent Systems

Homeworks for Multiagents course 

## Requirements 

* Needed python packages is in requirements.txt
```
 pip install -r requirements.txt
```
* Python version is $3.8.12$
* Prosody is used as XMPP server with self-signed certs
## How to generate certs:
```
prosodyctl cert generate $YOUR_ADRESS$ #as root then just hit Enter
cp /var/lib/prosody/$YOUR_ADRESS$.{key, crt, cnf} /etc/prosody/certs #as root
```
## Prosody config file
```
daemonize = true
pidfile = "/run/prosody/prosody.pid"
admins = { }
modules_enabled = {
		"disco";
		"roster";
		"saslauth";
		"tls";
		"blocklist";
		"bookmarks";
		"carbons";
		"dialback";
		"limits";
		"pep";
		"private";
		"smacks";
		"vcard4";
		"vcard_legacy";
		"csi_simple";
		"invites";
		"invites_adhoc";
		"invites_register";
		"ping";
		"register";
		"time";
		"uptime";
		"version";
		"admin_adhoc";
		"admin_shell";
}
modules_disabled = {
}

s2s_secure_auth = true

limits = {
	c2s = {
		rate = "10kb/s";
	};
	s2sin = {
		rate = "30kb/s";
	};
}

authentication = "internal_hashed"

allow_registration=true
archive_expires_after = "1w"
log = {
	info = "*syslog";
	}

certificates = "certs"

VirtualHost "127.0.0.1" 
```
 



