package z

import (
	"encoding/binary"
	"io"
)

// Header is the Z-Machine file header
type Header struct {
	Version byte
}

func (h *Header) Read(r io.Reader) {
	err := binary.Read(r, binary.LittleEndian, h)
	if err != nil {
		panic(err)
	}
}
