BEGIN {
    state = "guard"
}

# just print everything out when it's already released
/# v[0-9]+/ && NR == 1 && state == "guard" {
    state = "write"
}

# do not allow to release when there are open issues
/- \[ ?\] / && state == "guard" {
    print "not done" > "/dev/stderr"
    exit 1
}

# print increased version number in file header
/# v[0-9]+/ && NR > 1 && state == "guard" {
    gsub(/[^0-9]/, "")
    print "# v" ++$0

    state = "write"

    # rewind
    for (i = ARGC; i > ARGIND; i--) {
        ARGV[i] = ARGV[i-1]
    }
    ARGC++
    ARGV[ARGIND+1] = FILENAME
    nextfile
}

state == "write" {
    sub(/- \[.\] /, "") # remove checkboxes
    print
}
