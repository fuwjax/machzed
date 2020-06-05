package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/fuwjax/machzed/internal/z"
)

func main() {
	file, err := os.Open("docs/test/czech_0_8/czech.z5")
	if err != nil {
		panic(fmt.Sprintf("could not open file: %v", err))
	}
	story, err := z.ReadStory(file)
	if err != nil {
		panic(fmt.Sprintf("could not process header: %v", err))
	}
	obj, _ := json.Marshal(story.Dump())
	fmt.Println(string(obj))
}
