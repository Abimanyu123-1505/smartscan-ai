import os
import sys

def main():
    print("Setting up environment...")
    dirs = ['data/manifests', 'data/samples', 'scripts', 'tests']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("Directories created.")

if __name__ == "__main__":
    main()
