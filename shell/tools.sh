funic () {
 [[ $# -ne 1 ]] && echo "Invalid number of arguments" && return
 local char=$1
 [[ ${#char} -ne 1 ]] && echo "Invalid length ${#char}" && return
 echo -en "$char" | iconv -f utf-8 -t UNICODEBIG | xxd -g 2
}
