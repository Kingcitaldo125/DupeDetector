import argparse
import os

from collections import defaultdict
from hashlib import sha256
from sys import argv

def print_help():
    print("This is a script that can find duplicate files (same file content).")
    print("Duplicate files may also be optionally deleted.")
    print("Script can be ran like so:")
    print("python ccdupe.py [--min-size] <path_to_search>")

def main():
    # Instantiate an argument parser to help capture CLI args.
    parser = argparse.ArgumentParser(description="A script that can find duplicate files (same file content).")
    parser.add_argument("--min-size",type=int,help="A minimum size (bytes) for a file to be considered.")
    parser.add_argument(".",action="store_true",help="A minimum size (bytes) for a file to be considered.")
    args = parser.parse_args(argv[1:-1])

    # Need at least a directory to process
    if len(argv) < 2:
        print("Not enough arguments",argv)
        print_help()
        return

    # If the specified path/directory is not actually a directory, full stop
    xpath = argv[-1]
    if not os.path.isdir(xpath):
        print("Need to specify a directory")
        print_help()
        return

    hash_dict = defaultdict(list)
    dotdir_filter = lambda x: '.' in x and x != '.'
    file_max_size = 100_000
    # Search the specified directory for all duplicate files
    # Ignores 'dot' directories; e.g. '.git/'
    # Use SHA256 digests of file contents to determine file equivalence
    for path,dirs,files in os.walk(xpath):
        # Ignore dot directories
        dotlist = list(filter(dotdir_filter, path.split('/')))
        if len(dotlist) > 0:
            continue

        for f in files:
            jpath = os.path.join(path,f)
            # If this is not actually a file, for some reason, ignore
            if not os.path.exists(jpath):
                continue

            # If the size of the file in question is too big, or too small, ignore
            if args.min_size:
                fsize = os.path.getsize(jpath)
                if fsize < int(args.min_size) or fsize >= file_max_size:
                    continue

            #print(f"file: {jpath}")

            # Read the file
            contents = None
            try:
                with open(jpath) as fileobj:
                    contents = fileobj.read()
            except UnicodeDecodeError:
                pass

            # If we got some odd bytes from non-ascii files, ignore those files outright
            if not contents:
                continue

            # Get the file digest and add that file to the collection of files to be processed
            digest = sha256(contents.encode('utf-8')).hexdigest()
            hash_dict[digest].append(jpath)

    # Determine which duplicate files to delete (prompt user)
    deletion_candidates = set([])
    for k,v in hash_dict.items():
        if len(v) < 2:
            continue

        print("Found duplicate files:")
        for vv in v:
            print(vv)

        # Print out the listing of duplicate files for the user to optionally choose from
        idx = 1
        for vv in v:
            print(str(idx) + ") " + vv)
            idx += 1

        print("Select a file to delete (Any other value keeps the file and continues): ")
        choice = 0
        try:
            choice = int(input(''))
        except ValueError:
            pass

        # If this choice does not correspond to the listing of choices, just continue.
        # Non-integers are also not a valid choice
        if choice < 1 or choice > len(v):
            continue

        # Add the chosen file to a set of files to remove
        deletion_candidates.add(v[choice - 1])

    # Remove the chosen file(s)
    for candidate in deletion_candidates:
        os.remove(candidate)
        print(f"removed {candidate}")

if __name__ == "__main__":
    main()
