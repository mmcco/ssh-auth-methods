import subprocess, sys

# Should verbose be moved to main()?

def get_auth_methods(hostname, port=22, verbose=False):
    try:
        success_output = subprocess.check_output([
            'ssh',
            # prevents ominous error on changed host key
            '-o', 'StrictHostKeyChecking=no',
            # the point - prevents attempted authentication
            '-o', 'PreferredAuthentications=none',
            # prevents warning associated with unrecognized host key
            '-o', 'LogLevel=ERROR',
            '-p', str(port),
            # use root user to prevent leaking username
            'root@' + hostname,
            'exit'],    # the command to be executed upon success
            stderr=subprocess.STDOUT)
        # If we make it here, the server allowed us shell access without
        # authentication. Thankfully, the 'exit' command should have
        # left immediately.
        if verbose:
            print('Eek! Server allowed unauthenticated login! Exiting.')
        return ['none']
    # This is in fact the expected case, as we expect the SSH server to
    # reject the unauthenticated connection, and therefore expect exit code
    # 255, OpenSSH's sole error code.
    except subprocess.CalledProcessError as e:
        # ssh's result to stderr
        result = str(e.output.strip(), 'utf-8')

        if e.returncode != 255:
            if verbose:
                print('Eek! Server allowed unauthenticated login! '
                'Also, the command passed had a non-zero exit status.')
            return ['none']

        elif result.startswith('ssh: Could not resolve hostname'):
            if verbose:
                print('address resolution failed - '
                'maybe the server is down, '
                'the SSH server is on another port, '
                'or your IP is blacklisted?')
            raise Exception('resolution of address ' +  hostname + ' failed')

        elif result.startswith('Permission denied (') \
                and result.endswith(').'):
            # assume the format specified in the above condition with
            # comma-delimited auth methods
            return result[19:-2].split(',')

        else:
            raise Exception('unexpected SSH error response: ' + result)


def main():
    # the only two currently acceptable argument situations
    # a more complex argument system (using argparse, for example) may
    # be added later if needed.
    if len(sys.argv) == 1 or \
            len(sys.argv) == 2 and sys.argv[1] == '--verbose':
        verbose = len(sys.argv) == 2

        # loop through newline-delimited addresses
        for line in sys.stdin():
            hostname = line.strip()
            try:
                auth_methods = get_auth_methods(hostname, verbose=verbose)
            except:
                # could probably use a verbose print option there
                auth_methods = []

            print('\t'.join([hostname] + auth_methods))

    else:
        print('ERROR: input must be line-delimited hostnames from stdin',
                file=sys.stdin)
        print('usage: python3 ssh_password.py [-v]',
                file=sys.stdin)


if __name__ == '__main__':
    main()
