strace -f -e write -p1916 2>&1 | grep --color "\".*\""