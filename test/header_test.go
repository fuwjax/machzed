package machzed

import "testing"

func TestFirst(t *testing.T) {
	got := true
	if !got {
		t.Errorf("Abs(-1) = %v; want 1", got)
	}
}
