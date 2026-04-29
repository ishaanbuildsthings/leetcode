# Read from the file file.txt and output the tenth line to stdout.

# normally tail reads last 10
# -n sets the number of lines, + prefix flips to mean start from
# pipe symbol takes the output and redirects it to an input in the next command
# head prints first lines of something, -n 1 makes it just the first line
tail -n +10 file.txt | head -n 1