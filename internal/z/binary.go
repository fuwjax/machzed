package z

import (
	"io"
)

// Frame is a byte window that allows reads outside itself by masking only to a subset of data
// Note that Frame is very similar, but distinct from io.SectionReader
type Frame struct {
	file   io.ReaderAt
	start  int64
	length int
	err    error
}

func readBytesAt(file io.ReaderAt, length int, pos int64) (buffer []byte, err error) {
	buffer = make([]byte, length)
	_, err = file.ReadAt(buffer, pos)
	return
}

func readByteAt(file io.ReaderAt, pos int64) (value byte, err error) {
	bytes, err := readBytesAt(file, 1, pos)
	value = bytes[0]
	return
}

func readWordAt(file io.ReaderAt, pos int64) (value uint16, err error) {
	bytes, err := readBytesAt(file, 2, pos)
	value = uint16(bytes[0])*256 + uint16(bytes[1])
	return
}

func (frame Frame) Read(p []byte) (n int, err error) {
	return frame.ReadAt(p, 0)
}

// ReadAt implements io.ReaderAt.ReadAt
func (frame Frame) ReadAt(b []byte, off int64) (n int, err error) {
	if frame.err != nil || frame.length == 0 {
		return 0, frame.err
	}
	lie := 0
	if off < 0 {
		lie = int(0 - off)
		b = b[lie:]
		off = 0
	}
	if len(b) > frame.length {
		lie += len(b) - frame.length
		b = b[:frame.length]
	}
	n, err = frame.file.ReadAt(b, off+frame.start)
	// To match the ReaderAt interface, we adjust n by the number of elements requested outside the frame
	n += lie
	return
}
