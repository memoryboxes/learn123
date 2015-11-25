package main

import (
	"fmt"
	"os"
	"strings"
)

func main() {
	who := "world!"
	if len(os.Args) > 1 {
		who = strings.Join(os.Args[1:], " ")
	}
	fmt.Println("hello,来自", who)

	var i, j int = 1, 2
	k := 3
	fmt.Println(i, j, k)

	var f float64 = 1.23
	z := f
	fmt.Println(f, z)
}
