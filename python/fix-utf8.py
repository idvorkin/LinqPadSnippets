import sys
import ftfy


def fix_file(file_path):
    with open(file_path, "r+") as f:
        text = f.read()
        f.seek(0)
        f.write(ftfy.fix_text(text))
        f.truncate()


def main():
    for path in sys.argv[1:]:
        print(">>> ", path)
        fix_file(path)


if __name__ == "__main__":
    main()
