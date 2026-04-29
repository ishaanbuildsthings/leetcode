# Read from the file words.txt and output the word frequency list to stdout.


# awk is like a program and we pass the program with 'program'
# awk processes each line one at a time, it splits words by space already

awk '
{
    # NF is a built-in awk variable: "number of fields" on the current line.
    # If the line is "the day is sunny", then NF is 4.
    # We loop i from 1 to NF (awk fields are 1-indexed, not 0-indexed).

    # NF is built in, its # of fields on a current line
    for (i = 1; i <= NF; i++) {
        # $i is a builtin for the i-th field (1-indexed)
        # count isnt a special name, its auto-created and auto-zeroed the first time we use it
        count[$i]++
    }
}

# END block runs once after every line processes
END {
    for (word in count) {
        print word, count[word]
    }
}
# pipe results into a sort, -k2 sorts by second column, -rn means reverse order and numeric based not string based
' words.txt | sort -k2 -rn