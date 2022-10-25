import os
import sys
import shutil
import csv
import re
import subprocess

# process all PDF files in the named directory

# create directories and move files into them
# run pdftk on each to split
# remove extraneous files
# produce CSV


def process_replacements(s, replacements):
    for r in replacements:
        pattern, replacement = r.split("/")
        s = re.sub(pattern, replacement, s)
    return s


def produce_csv(workdir, replacements):
    csv_filepath = os.path.join(workdir, 'metadata.csv')
    writer = csv.writer(open(csv_filepath, 'w'))
    writer.writerow(['id', 'title', 'field_model', 'field_display_hints'])
    rows = 0
    for filepath in os.listdir(workdir):
        full_filepath = os.path.join(workdir, filepath)
        if not os.path.isfile(full_filepath) or not filepath.lower().endswith('.pdf'):
            continue
        id = filepath[:-4]
        title = process_replacements(id, replacements)
        writer.writerow([id, title, "Paged Content", "1"])
        rows += 1
    print('Created metadata.csv and populated it with %d records' % rows)


def process_files(workdir):
    files = 0
    errors = 0
    for filepath in os.listdir(workdir):
        full_filepath = os.path.join(workdir, filepath)
        if not os.path.isfile(full_filepath) or not filepath.lower().endswith('.pdf'):
            continue

        # move PDF into subdirectory
        dirpath = os.path.join(workdir, filepath[:-4])
        os.mkdir(dirpath)
        shutil.move(full_filepath, dirpath)

        # split into pages
        p = subprocess.run("pdftk '%s' burst output page-%%02d.pdf" % filepath, 
                           cwd=os.path.join(os.getcwd(), dirpath), shell=True, capture_output=True, universal_newlines=True)
        if p.returncode != 0:
            print("pdftk returned an error processing %s:" % filepath)
            print(p.stdout)
            print(p.stderr)
            print("\n")
            errors += 1
        else:
            docdata = os.path.join(dirpath, 'doc_data.txt')
            if os.path.exists(dirpath):
                os.unlink(docdata)
            os.unlink(os.path.join(dirpath, filepath))
        files += 1

    print('Processed %d files.' % files)
    if errors:
        print('Errors occurred on %d files.  Check the above output for errors/clues.  Once you find the issue it is probably best to start again fresh.' % errors)


workdir = sys.argv[1]
if os.path.exists(os.path.join(workdir, 'metadata.csv')):
    print("metadata.csv already exists. Aborting.")
    sys.exit(1)
produce_csv(workdir, sys.argv[2:])
process_files(workdir)
