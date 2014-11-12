ssh-auth-methods
================

A simple Python 3 script and package that returns a list of the
authentication methods supported by an SSH server.

No non-standard Python packages are required.

**WARNING:** *The IP address that you run this script on can get blocked
or even blacklisted! Use with caution. (See the _Warnings_ section below
for more info).*

## Use

The next two subsections assume that you're using this as
a stand-alone shell script. The functions can be imported to Python 3
code. See the section *Library* for a discussion of this.

### Input

The script reads from standard input. To test Google, you can simply use:

`echo 'google.com' | python3 ssh_auth_methods.py`

The input can be domain names or IP addresses.

Multiple inputs are expected to be line-delimited. To test each
in a file of line-delimited addresses, simply use:

`cat my_addrs.txt | python3 ssh_auth_methods.py`

### Output

The ouput is one address per line. Each line is tab-delimited, with
the supplied address as its first field, followed by each authentication method
supported by the corresponding SSH server.

Nothing is printed after the address if the address
could not be resolved, the request timed out,
or that there was an error parsing the response received.

The script is threaded, so outputs will be printing as they are received
and processed.

The auth method 'none' implies that the SSH server let us in without any
authentication at all. 
Our SSH command ends in `'exit'` so that we'll disconnect immediately
if granted access. In this case, we can't find what the other potential auth methods
are (nor do they really matter), so 'none' will be the only one returned.
Additionally, we assume that any non-error (i.e. not `255`) SSH exit status
means the login was successful. This is because `255` is OpenSSH's only
error status, and all other statuses are those of the remotely executed
command (see OpenSSH man pages).

### Library

The core function in this module is `get_auth_methods()`. It takes the
hostname scanned, an optional port number (defaulting to `22`), a default
SSH request timeout (defaulting to 5.0), and a
boolean determining verbosity (defaulting to False).

`threaded_auth_methods()` takes a file containing newline-delimited
hostnames and spawns a thread executing `get_auth_methods()` for each
of them. I'll leave out specific argument descriptions, as the code
should be self-documenting.

## Warning

SSH protection software like [SSHGuard](http://www.sshguard.net/) and
[fail2ban](http://www.fail2ban.org/wiki/index.php/Main_Page) will
probably find your requests suspect even though they don't attempt to
feign authentication. I know SSHGuard does, as some of my own servers
started blocking my test server. This may even lead to the IP address
used being added to a blacklist if this software reports offenders. So,
exercise restraint, and consider using a [dirt-cheap VPS](http://lowendbox.com/).

As with all security scanning software, there is potential to make
people suspicious or angry if you don't give them prior warning. Despite
this being a particularly harmless breed, I should probably clarify that
I don't offer this script for nefarious or illegal use. For everything
you need to know about liability, see the included license.

## Dependencies

This currently only runs on Python 3. Because the code is relatively
small and simple, porting should be pretty easy.

As mentioned in the *Output* section, using an SSH client other than OpenSSH
may cause unpredictable results because of exit statuses. Namely, if
failed authentication is ever indicated by an exit status other than `255`,
a servers will be falsely reported as allowing unauthenticated login.

## Background

[This StackOverflow post](http://stackoverflow.com/questions/3585586/how-can-i-programmatically-detect-ssh-authentication-types-available)
tipped me off to the fact that the SSH Authentication Protocol
([RFC 4252](https://www.ietf.org/rfc/rfc4252.txt)) suggests a slightly
hacky way of finding which authentication methods an SSH server offers:

> Authentication methods are identified by their name, as defined in [SSH-ARCH]. The "none" method is reserved, and MUST NOT be listed as supported. However, it MAY be sent by the client. The server MUST always reject this request, unless the client is to be granted access without any authentication, in which case, the server MUST accept this request. The main purpose of sending this request is to get the list of supported methods from the server.

SSH servers traditionally offer little information about their
configuration for security reasons, so this isn't surprising.

Specifically, if the client's `PreferredAuthentications` option is set to `none`
and the server requires authentication, it is supposed to reject the request and supply a list of
supported auth methods. In short, this script makes such a request and
parses the supported auth methods out of the response.

## Why?

The short answer is that I wanted to do a security scan of Tor relays
to begin publicly auditing the network's security.

More generally, it's valuable to know which authentication methods a
server supports, as some are far weaker than others. Generally, you
should only support public-key authentication unless you have a very
good reason to do otherwise.

This tool, like nmap et al., is useful for scanning your own servers.
You may find that one of your machine's `/etc/ssh/sshd_config` options
weren't what you thought, or even that you forgot to restart `sshd`
after changing them. I did.

## Quirks

The timeout mechanism used with Python 3.3+ is different from that used
with older versions. The optional `timeout` argument was added to
`subprocess.check_output()` in Python 3.3. With older versions of
Python, we instead use the `ConnectTimeout` SSH option. This allows
the specified timeout for every IP address associated with a domain
name, so something like `google.com` will take significantly longer
than the supplied timeout.

I think the `subprocess.check_output()` timeout is probably preferable;
if we haven't heard back from the server in five or so seconds, we
probably aren't getting a response. However, there is no easy way
to implement this in earlier versions of Python, aside perhaps from
making the user install the `subprocess32` package.
