# Read from the file file.txt and output all valid phone numbers to stdout.

# grep searches for lines matching a pattern, automatically reads in every line and outputs every line
# -E gives extended matching
# the middle part is just a regex i stole from online lol
grep -E '^([0-9]{3}-|\([0-9]{3}\) )[0-9]{3}-[0-9]{4}$' file.txt