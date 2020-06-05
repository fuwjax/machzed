package z

import "fmt"

// Version is the Z-Machine version of a story file
type Version interface {
	headerFrame(*Story) Frame
	extendedHeaderFrame(*Story) Frame
	maxFileLength() int
	size(*Story) int

	// It is unlikely the following two methods will exist as is. They are here mostly for documenting section 1
	routineAddress(*Story, uint16) int
	stringAddress(*Story, uint16) int
}

func version(versionNumber byte) (Version, error) {
	switch versionNumber {
	case 5:
		return version5{}, nil
	}
	return nil, fmt.Errorf("No version for %d", versionNumber)
}

type version5 struct {
}

func (v version5) headerFrame(story *Story) (frame Frame) {
	return Frame{story.file, 0, 0x38, nil} // v6+ is 0x40
}

func (v version5) extendedHeaderFrame(story *Story) Frame {
	if story.header.HeaderExtensionAddress > 0 {
		length, err := readWordAt(story.file, int64(story.header.HeaderExtensionAddress))
		start := int64(story.header.HeaderExtensionAddress + 2)
		return Frame{story.file, start, 2 * int(length), err}
	}
	return Frame{}
}

func (v version5) maxFileLength() int {
	return 256 // units? // 1-3: 128, 4-5: 256, 6-8: 512
}

func (v version5) size(story *Story) int {
	return 4 * int(story.header.FileLength)
}

func (v version5) routineAddress(story *Story, packAddr uint16) int {
	return int(packAddr) * 4 // RoutinesAddress  not used until v6
}

func (v version5) stringAddress(story *Story, packAddr uint16) int {
	return int(packAddr) * 4 // StaticStringsAddress not used until v6
}
