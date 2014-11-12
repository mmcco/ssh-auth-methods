ssh-auth-methods
================

A simple Python 3 script and package that returns a list of the
authentication methods supported by an SSH server.

Usable library functions are included, as well as a Unix-compliant
threaded script.

No non-standard Python packages are required.

**WARNING** *This is in heavy development as of Nov. 11, 2014. Don't
trust it yet!*

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

Nothing is printed after the address in the case that the address
could not be contacted, or that there was an error parsing the response
received.

The auth method 'none' implies that the SSH server let us in without any
authentication at all. I suspect this is possible, although I haven't encountered
it. The SSH command ends in `'exit'` so that we'll disconnect immediately
if granted access. In this case, we can't find what the other potential auth methods
are (nor do they really matter), so 'none' will be the only one returned.
Additionally, we assume that any non-error (i.e. not `255`) SSH exit status
means the login was successful. This is because 255 is OpenSSH's only
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

## Dependencies

This currently only runs on Python 3. Because the code is relatively
small and simple, porting should be pretty easy.

As mentioned in the *Output* section, using an SSH client other than OpenSSH
may cause unpredictable results because of exit statuses. Namely, if
failed authentication is ever indicated by an exit status other than `255`,
a servers will be falsely reported as allowing unauthenticated login.

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
