import subprocess, sys, threading
from queue import Queue

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
            'root@' + hostname,    # use root user to prevent leaking username
            'exit'],    # the command to be executed upon successful auth
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
                print('hostname resolution failed - '
                'maybe the server is down, '
                'the SSH server is on another port, '
                'or your IP is blacklisted?')
            raise Exception('resolution of hostname ' +  hostname + ' failed')

        elif result.startswith('Permission denied (') \
                and result.endswith(').'):
            # assume the format specified in the above condition with
            # comma-delimited auth methods
            return result[19:-2].split(',')

        else:
            raise Exception('unexpected SSH error response: ' + result)


def _ssh_worker(host_queue, response_queue, timeout, ssh_args):
    
    hostname = host_queue.get()
    try:
        resp = get_auth_methods(hostname, **ssh_args)
    except:
        resp = None

    response_queue.put((hostname, resp))
    host_queue.task_done()


def _threaded_auth_methods(host_file, timeout=5, verbose=False):
    # All get_auth_methods() args aside from hostname are optional,
    # and are the same across all calls.
    # We therefore use a dict of args that is unpacked in calls.
    ssh_args = {'verbose': verbose}
    host_queue, response_queue = Queue(), Queue()

    num_hosts = 0

    for line in host_file:
        num_hosts += 1
        host_queue.put(line.strip())
        t = threading.Thread(
                target=_ssh_worker,
                args=[host_queue, response_queue, timeout, ssh_args])
        t.daemon = True
        t.start()

    host_queue.join()

    return [response_queue.get() for _ in range(num_hosts)]


def main():
    # the only two currently acceptable argument situations
    # a more complex argument system (using argparse, for example) may
    # be added later if needed.
    if len(sys.argv) == 1 or \
            len(sys.argv) == 2 and sys.argv[1] == '--verbose':
        verbose = len(sys.argv) == 2

        '''
        # loop through newline-delimited hostnames
        for line in sys.stdin:
            hostname = line.strip()
            try:
                auth_methods = get_auth_methods(hostname, verbose=verbose)
            except:
                # could probably use a verbose print option there
                auth_methods = []

            print('\t'.join([hostname] + auth_methods))
        '''

        response_tups = _threaded_auth_methods(sys.stdin, verbose=verbose)

        for hostname, methods in response_tups:
            print('\t'.join([hostname] + methods))

    else:
        print('ERROR: input must be line-delimited hostnames from stdin',
                file=sys.stdin)
        print('usage: python3 ssh_password.py [-v]',
                file=sys.stdin)


if __name__ == '__main__':
    main()
