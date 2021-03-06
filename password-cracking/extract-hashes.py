#!/usr/bin/python3
import os, argparse, sys, time, re
from datetime import timedelta
try:
    import tqdm
except:
    print("Please install tqdm 'pip3 install tqdm' for an awesome progress bar.")
    sys.exit()

#############################           Global Variable Declarations           #############################

GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
ENDC = '\033[0m'
okBox = BLUE +      '[*]      ' + ENDC
noteBox = GREEN +   '[+]      ' + ENDC
failBox = RED +     '[!]      ' + ENDC

emailRegex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
md5Regex = r'[^a-z^A-Z^0-9]([a-f0-9]{32}|[A-F0-9]{32})[^a-z^A-Z^0-9]'

parser = argparse.ArgumentParser()
parser.add_argument('inFile', type=str, help='Raw dump file.', action='store')
parser.add_argument('outFile', type=str, help='Cleaned output file', action='store')
args = parser.parse_args()
inFile = args.inFile
outFile = args.outFile

#############################         End Global Variable Declarations          #############################

"""
If you are customizing this script for a particular password dump, probably all you need to do is:
    1. In the 'Global Variable Declarations' above, define a regex for the hash type you have in the file.
    2. Modify the 'customClean' function below to meet your needs.
"""

def customClean(line):
    """
    This is the custom function for a particular password dump.
    It could probably be used as is for other similar dumps, or modified as needed.
    It will look for lines that have an email address and something that looks like an MD5 hash. Th regex below grabs the FIRST thing 
    that looks like an email and the LAST thing that looks like a hash on each line. It then sends a write to the outFile like this:
        someone@mail.com:33c5d4954da881814420f3ba39772644
    """
    try:
        email = re.findall(emailRegex, line)[0]
        md5Hash = re.findall(md5Regex, line)[-1]
        cleanLine = email + ":" + md5Hash + "\n"
        return cleanLine
    except:
        return False

def getLines(fN):
    """
    This function runs before any transformation.
    It is used to count the lines in the source file so that an accurate progress bar can be displayed.
    """
    try:
        fileSize = str((os.path.getsize(fN)/1000000))
        print(okBox + "Counting lines in {}: {}MB".format(fN, fileSize))
        lines = os.popen('wc -l ' + fN).read().split()[0]
        print(okBox + "    ....Found {} lines.\n\n".format(lines))
        return int(lines)
    except Exception:
        print(failBox + "Could not open {}.".format(fN))
        sys.exit()

def processFile(inFile, outFile):
    """
    This is the core function to read lines in from the file and display a progress.
    This function should pass each individual line to the custom function for the particular type of password dump you are processing.
    No actual transformation happens inside this function itself.
    """
    totalLines = getLines(inFile)
    newLines = 0
    with tqdm.tqdm(total=totalLines, unit=' lines', desc='Progress', dynamic_ncols='True') as pbar:
        with open(inFile, errors='ignore') as pF:
            for line in pF:
                cleanLine = customClean(line)
                if cleanLine:
                    outFile.write(cleanLine)
                    newLines += 1
                pbar.update(1)
            pF.close()
    return newLines


def main():
    start = time.time()
    print("Reading from " + inFile + ": " + str((int(os.path.getsize(inFile)/1000000))) + " MB")
    with open(outFile, 'a') as oF:
        newLines = processFile(inFile, oF)
        oF.close()
    elapsed = (time.time() - start)
    elapsedTime = str(timedelta(seconds=elapsed))
    print("\n\n" + noteBox + "All done! Wrote {} lines to {}. Elapsed time: {}.".format(newLines, outFile, elapsedTime))

if __name__ == "__main__":
    main()

