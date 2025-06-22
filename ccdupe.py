import os

from collections import defaultdict
from hashlib import sha256
from sys import argv

def print_help():
    print("This is a script that can find duplicate files (same file content).")
    print("Duplicate files may also be optionally deleted.")
    print("Script can be ran like so:")
    print("python ccdupe.py <path_to_search>")

def main():
    if len(argv) != 2:
        print_help()
        return

    xpath = argv[1]
    if not os.path.isdir(xpath):
        print("Need to specify a directory")
        print_help()
        return

    hash_dict = defaultdict(list)
    dotdir_filter = lambda x: '.' in x and x != '.'
    for path,dirs,files in os.walk(xpath):
        # Ignore dot directories
        dotlist = list(filter(dotdir_filter, path.split('/')))
        if len(dotlist) > 0:
            continue

        for f in files:
            jpath = os.path.join(path,f)
            if not os.path.exists(jpath):
                continue

            #print(f"file: {jpath}")
            contents = None

            try:
                with open(jpath) as fileobj:
                    contents = fileobj.read()
            except UnicodeDecodeError:
                pass

            if not contents:
                continue

            digest = sha256(contents.encode('utf-8')).hexdigest()
            hash_dict[digest].append(jpath)

    deletion_candidates = set([])
    for k,v in hash_dict.items():
        if len(v) < 2:
            continue

        print("Found duplicate files:")
        for vv in v:
            print(vv)

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

        if choice < 1 or choice > len(v):
            continue

        deletion_candidates.add(v[choice - 1])

    for candidate in deletion_candidates:
        os.remove(candidate)
        print(f"removed {candidate}")

if __name__ == "__main__":
    main()
