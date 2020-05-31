package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/fuwjax/machzed/internal/z"
)

func main() {
	header := z.StoryFileHeader{}
	file, err := os.Open("docs/test/czech_0_8/czech.z5")
	if err != nil {
		panic("could not open file")
	}
	extHeader, err := header.Read(file)
	if err != nil {
		panic("could not process header")
	}
	headerObj, _ := json.Marshal(header)
	fmt.Println(string(headerObj))
	extHeaderObj, _ := json.Marshal(extHeader)
	fmt.Println(string(extHeaderObj))
}
