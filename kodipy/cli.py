import argparse

from kodipy import KodiInterface


def main():
    parser = argparse.ArgumentParser(description='control Kodi')
    parser.add_argument(
        '--config', dest='configfile', action='store', nargs='?')
    parser.add_argument(
        '--name', dest='sectioname', action='store', nargs='?')
    parser.add_argument('--host', dest='host', action='store', nargs='?')
    parser.add_argument('--port', dest='port', action='store', nargs='?')
    parser.add_argument(
        '--username', dest='username', action='store', nargs='?')
    parser.add_argument(
        '--password', dest='password', action='store', nargs='?')
    args = parser.parse_args()
    kodi = KodiInterface(**vars(args))
    kodi.introspect()

if __name__ == "__main__":
    main()
