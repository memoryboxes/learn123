package main

import (
	"bytes"
	"fmt"
)

func main() {
	test_stringA := `hello",world`
	test_stringA += "new world"
	test_stringB := test_stringA
	test_string_len := "中国"

	fmt.Println(test_stringA[1])
	fmt.Println(test_stringA)
	fmt.Println(test_stringB)
	fmt.Println(test_stringB == test_stringA)
	fmt.Println(len([]rune(test_string_len)))
	fmt.Println(len(test_string_len))

	test_buffer()
}

func test_buffer() {
	var buffer bytes.Buffer
	buffer.WriteString("hello\n")
	buffer.WriteString("world")
	fmt.Print(buffer.String(), "\n")

	//p := polar(8.32, .49)
	fmt.Print(-18.5, 17, "elephant", -8+.7i, 0x3C7, '\u03c7', "a", "b")
}
