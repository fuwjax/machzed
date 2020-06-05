package z

import (
	"encoding/binary"
	"io"
	"math"
	"os"
)

// Story is the in-memory representation of a z-machine story file.
// It is the exported member of the Z package, and should be the only interface external consumers of this package need.
type Story struct {
	file      io.ReaderAt
	size      int
	version   Version
	header    StoryFileHeader
	extHeader StoryFileExtendedHeader
}

// ReadStory reads a story from a z-machine file
func ReadStory(input io.ReaderAt) (story Story, err error) {
	story = Story{file: input, header: StoryFileHeader{}, extHeader: StoryFileExtendedHeader{}}
	file, ok := input.(*os.File)
	if ok {
		stat, err := file.Stat()
		if err == nil {
			story.size = int(stat.Size())
		}
	}
	versionNumber, err := readByteAt(input, 0)
	if err != nil {
		return
	}
	story.version, err = version(versionNumber)
	if err != nil {
		return
	}
	err = binary.Read(story.version.headerFrame(&story), binary.BigEndian, &story.header)
	if err != nil {
		return
	}
	err = binary.Read(story.version.extendedHeaderFrame(&story), binary.BigEndian, &story.extHeader)
	return
}

// Version is the version number of the story file format
func (story *Story) Version() int {
	return int(story.header.Version)
}

// Size is the file size in bytes of the story's storyfile
func (story *Story) Size() int {
	if story.size > 0 {
		return story.size
	}
	return story.version.size(story)
}

// DynamicMemoryFrame is the dynamic memory as defined in section 1.1
func (story *Story) DynamicMemoryFrame() Frame {
	return Frame{story.file, 0, int(story.header.StaticMemoryAddress), nil}
}

// StaticMemoryFrame is the static memory as defined in section 1.1
func (story *Story) StaticMemoryFrame() Frame {
	limit := int(math.Min(0xFFFF, float64(story.Size())))
	return Frame{story.file, int64(story.header.StaticMemoryAddress), limit - int(story.header.StaticMemoryAddress), nil}
}

// HighMemoryFrame is the high memory as defined in section 1.1
func (story *Story) HighMemoryFrame() Frame {
	return Frame{story.file, int64(story.header.HighMemoryBaseAddress), story.Size() - int(story.header.HighMemoryBaseAddress), nil}
}

// Dump returns a json-marshal-able map of internal data
func (story *Story) Dump() interface{} {
	obj := make(map[string]interface{})
	obj["header"] = story.header
	obj["extHeader"] = story.extHeader
	obj["size"] = story.Size()
	return obj
}
