# Read from the file file.txt and print its transposed content to stdout.

awk '
{
    # number of fields in the current line, automatically ran on every line
    # basically looping over columns here
    for (i = 1; i <= NF; i++) {
        # first line number we dont use a space, we store everything left aligned
        if (NR == 1) {
            row[i] = $i
        } 
        # afterwards we append the datum
        else {
            row[i] = row[i] " " $i
        }
    }
}
END {
    for (i = 1; i <= NF; i++) {
        print row[i]
    }
}
' file.txt