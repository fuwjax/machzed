package z_test

import (
	"os"
	"testing"

	"github.com/fuwjax/machzed/internal/z"
)

func TestFirst(t *testing.T) {
	header := z.Header{}
	file, err := os.Open("data/czech.z5")
	if err != nil {
		t.Errorf("could not open file")
	}
	header.Read(file)
	if header.Version != 5 {
		t.Errorf("Unexpected version %v", header.Version)
	}
}
