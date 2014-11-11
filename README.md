ssh-auth-methods
================

A simple, single-function Python 3 script that returns a list of the authentication methods supported by an SSH server.

## Use

The next two subsections assume that you're using this script as
a stand-alone shell script. The function can be imported to Python 3
code. See the section *Function* for a discussion of this.

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

### Function

The sole function in this module is `get_auth_methods()`. It takes the
hostname scanned, an optional port number (defaulting to 22), and a
boolean determining verbosity (defaulting to False).

## Dependencies

This currently only runs on Python 3. It's short and simple, so porting it should be simple.
I may do so myself at some point if people use this.
