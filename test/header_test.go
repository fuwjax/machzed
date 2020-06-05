package z_test

import (
	"os"
	"testing"

	"github.com/fuwjax/machzed/internal/z"
)

func TestFirst(t *testing.T) {
	file, err := os.Open("data/czech.z5")
	if err != nil {
		t.Errorf("could not open file")
	}
	story, err := z.ReadStory(file)
	if err != nil {
		t.Errorf("could not read story")
	}
	if story.Version() != 5 {
		t.Errorf("Unexpected version %v", story.Version())
	}
}
