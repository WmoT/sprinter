"""
The install script for a sprinter-based setup script.
"""
import logging
import os
import signal
import sys
from optparse import OptionParser

from sprinter import lib
from sprinter.environment import Environment

description = \
"""
Install an environment as specified in a sprinter config file
"""

VALID_COMMANDS = ["install", "update", "environments", "validate",
                  "remove", "deactivate", "activate", "reload"]

parser = OptionParser(description=description)
# parser = argparse.ArgumentParser(description=description)
# parser.add_option('command', metavar='C',
#                     help="The operation that sprinter should run (install, deactivate, activate, switch)")
# parser.add_option('target', metavar='T', help="The path to the manifest file to install", nargs='?')
parser.add_option('--namespace', dest='namespace', default=None,
                    help="Namespace to check environment against")
parser.add_option('--username', dest='username', default=None,
                    help="Username if the url requires authentication")
parser.add_option('--auth', dest='auth', action='store_true',
                    help="Specifies authentication is required")
parser.add_option('--password', dest='password', default=None,
                    help="Password if the url requires authentication")
parser.add_option('-v', dest='verbose', action='store_true', help="Make output verbose")
# not implemented yet
parser.add_option('--sandboxbrew', dest='sandbox_brew', default=False,
                    help="if true, sandbox a brew installation, alternatively, " + \
                         "false will disable brew sandboxes for configuration that request it.")
parser.add_option('--sandboxaptget', dest='sandbox_aptget', default=False,
                    help="if true, sandbox an apt-get installation, alternatively, " +
                         "false will disable apt-get sandboxes for configuration that request it.")
parser.add_option('--virtualenv', dest='virtualenv', default=False,
                    help="if true, will virtualenv sprinter and install eggs relative to it, " +
                         "false will disable apt-get sandboxes for configuration that request it.")

def signal_handler(signal, frame):
    print "Shutting down sprinter..."
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parse_args(sys.argv[1:])


def error(message):
    print message
    exit()


def parse_args(argv, Environment=Environment):
    options, args = parser.parse_args(argv)
    if len(args) == 0:
        error("Please enter a sprinter action: %s" % str(VALID_COMMANDS))
    command = args[0].lower()
    if command not in VALID_COMMANDS:
        error("Please enter a valid sprinter action: %s" % str(VALID_COMMANDS))
    target = args[1] if len(args) > 1 else None
    logging_level = logging.DEBUG if options.verbose else logging.INFO
    env = Environment(logging_level=logging_level)

    if command == "environments":
        SPRINTER_ROOT = os.path.expanduser(os.path.join("~", ".sprinter"))
        for env in os.listdir(SPRINTER_ROOT):
            print "%s" % env

    # these commands need an target
    if target is None:
        error("Please enter a target!")

    if command in ('remove', 'deactivate', 'activate', 'reload'):
        getattr(env, command)(target)

    elif command == "install":
        if options.username or options.auth:
            if not options.username:
                options.username = lib.prompt("Please enter the username for %s..." % parse_domain(target))
            if not options.password:
                options.password = lib.prompt("Please enter the password for %s..." % parse_domain(target), secret=True)
        env.install(target,
                  namespace=options.namespace,
                  username=options.username,
                  password=options.password)

    elif command == "update":
        if options.username or options.auth:
            if not options.username:
                options.username = lib.prompt("Please enter the username for %s..." % target)
            if not options.password:
                options.password = lib.prompt("Please enter the password for %s..." % target, secret=True)
        env.update(target, username=options.username, password=options.password)

    elif command == "validate":
        if options.username or options.auth:
            if not options.username:
                options.username = lib.prompt("Please enter the username for the sprinter url...")
            if not options.password:
                options.password = lib.prompt("Please enter the password for the sprinter url...", secret=True)
        errors = env.validate_manifest(target, username=options.username, password=options.password)
        if len(errors) > 0:
            print "Manifest is invalid!"
            print "\n".join(errors)
        else:
            print "Manifest is valid!"


def parse_domain(url):
    """ parse the domain from the url """
    domain_match = lib.DOMAIN_REGEX.match(url)
    if domain_match:
        return domain_match.group()

if __name__ == '__main__':
    main()
