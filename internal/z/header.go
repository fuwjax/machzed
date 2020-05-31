package z

import (
	"encoding/binary"
	"fmt"
)

func safe(err error) {
	if err != nil {
		panic(err)
	}
}

//StoryFile represents the story data as an extended Reader and ReaderAt. An io.File is a StoryFile
type StoryFile interface {
	Read(p []byte) (n int, err error)
	Seek(offset int64, whence int) (ret int64, err error)
	ReadAt(b []byte, off int64) (n int, err error)
}

type Frame struct {
	story StoryFile
	start int64
	end   int64
}

func frame(story StoryFile, pos uint16) (frame Frame, err error) {
	_, err = story.Seek(int64(pos), 0)
	if err != nil {
		return
	}
	buffer := make([]byte, 2)
	n, err := story.Read(buffer)
	if n != 2 {
		err = fmt.Errorf("expected 2 bytes, received %d", n)
	} else if err == nil {
		start := int64(pos + 2)
		length := int64(buffer[0])*256 + int64(buffer[1])
		frame = Frame{story, start, start + length}
	}
	return
}

// Read implements StoryFile.Read
func (frame Frame) Read(p []byte) (n int, err error) {
	storyOffset, err := frame.story.Seek(0, 1)
	if storyOffset < frame.start || storyOffset >= frame.end {
		err = fmt.Errorf("Read offset outside of Frame, seek first")
	} else {
		remaining := frame.end - storyOffset
		originalLength := len(p)
		if int64(originalLength) > remaining {
			p = p[:remaining]
		}
		n, err = frame.story.Read(p)
		p = p[:originalLength]
	}
	return
}

// Seek implements StoryFile.Seek
func (frame Frame) Seek(offset int64, whence int) (ret int64, err error) {
	switch whence {
	case 0:
		ret, err = frame.story.Seek(frame.start+offset, 0)
	case 1:
		ret, err = frame.story.Seek(offset, 1)
	case 2:
		ret, err = frame.story.Seek(frame.end+offset, 2)
	}
	return
}

// ReadAt implements StoryFile.ReadAt
func (frame Frame) ReadAt(b []byte, off int64) (n int, err error) {
	_, err = frame.Seek(off, 0)
	if err == nil {
		n, err = frame.Read(b)
	}
	return
}

// StoryFileHeader is the Z-Machine file header
type StoryFileHeader struct {
	Version                      byte
	Flags1                       byte
	ReleaseNumber                uint16
	HighMemoryBaseAddress        uint16
	ProgramStartAddress          uint16
	DictionaryAddress            uint16
	ObjectsAddress               uint16
	GlobalVariablesAddress       uint16
	StaticMemoryAddress          uint16
	Flags2                       uint16
	SerialCode                   [6]byte
	AbbreviationsAddress         uint16
	FileLength                   uint16
	FileChecksum                 uint16
	InterpreterNumber            byte
	InterpreterVersion           byte
	ScreenHeight                 byte
	ScreenWidth                  byte
	ScreenWidthUnits             uint16
	ScreenHeightUnits            uint16
	FontHeightUnits              byte
	FontWidthUnits               byte
	RoutinesAddress              uint16
	StaticStringsAddress         uint16
	DefaultBackgroundColor       byte
	DefaultForegroundColor       byte
	TerminatingCharactersAddress uint16
	OutputStream3Width           uint16
	RevisionNumber               uint16
	AlphabetAddress              uint16
	HeaderExtensionAddress       uint16
	User                         [8]byte
	CompilerVersion              [4]byte
}

// StoryFileExtendedHeader is the Z-Machine extended file header from version 5-8
type StoryFileExtendedHeader struct {
	MouseX                     uint16
	MouseY                     uint16
	UnicodeTranslationAddress  uint16
	Flags3                     uint16
	TrueDefaultForegroundColor uint16
	TrueDefaultBackgroundColor uint16
}

// type Story struct {
// 	version Version
// 	header  *StoryFileHeader
//   extHeader *StoryFileExtendedHeader
// }

// GameConfig is the set of header flags that a game may initialize with.
// it may not be a useful interface, it is included primarily for documentation
type GameConfig interface {
	//  flags1 bit 1 versions 1-3, true if "score/turns", false if "hours:mins"
	HasTimerStatusLine() bool
	// flags1 bit 2 versions 1-3, true if story split across discs (files), false otherwise
	HasSplitStoryFile() bool
	// flags2 bit 3 versions 5-8, true if story uses pictures
	UsesPicture() bool
	// flags2 bit 4 versions 5-8, true if story uses UNDO opcodes. In version 3 it may have signaled the use of sounds
	UsesUndo() bool
	// flags2 bit 5 versions 5-8, true if story uses mouse
	UsesMouse() bool
	// flags2 bit 6 versions 5-8, true if story uses color
	UsesColor() bool
	// flags2 bit 7 versions 5-8, true if story uses sound effects
	UsesSound() bool
	// flags2 bit 8 versions 6-8, true if story uses menu
	UsesMenu() bool
	// flags3 bit 0 versions 6-8, true if story uses transparency
	UsesTransparency() bool
}

//GameStatus is the set of header flags that a game may alter.
//it may not be a useful interface, it is included primarily for documentation
type GameStatus interface {
	// flags2 bit 0 versions 1-8, true if story turns on transcripting, false if it turns off
	EnableTranscripting(state bool)
	// flags2 bit 0 versions 1-8, true if transcripting is on, false otherwise
	TranscriptingEnabled() bool
	// flags2 bit 10 versions ?, possibly true if interpreter encountered an error during transcription, false otherwise
	TranscriptingError() bool
	// flags2 bit 1 versions 3-8, true if story turns on fixed pitch fonts, false if it turns them off
	EnableFixedPitch(state bool)
	// flags2 bit 1 versions 3-8, true if fixed-pitch is on, false otherwise
	FixedPitchEnabled() bool
	// flags2 bit 0 versions 6-8, true if interpreter wants screen redrawn, false otherwise
	RefreshScreen() bool
	// flags2 bit 0 versions 6-8, called by game to inform interpreter screen was redrawn
	ScreenRefreshed()
}

//Capabilities is the set of header flags (and psuedo-flags) that the interpreter exposes to games through the header.
//it may not be a useful interface, it is included primarily for documentation
type Capabilities interface {
	// flags1 bit 3 version 3, true if interpreter requests censorship, false otherwise (TandyBit)
	IsCensored() bool
	// flags1 bit 4 versions 1-3, true if interpreter supports status line, false otherwise
	CanStatusLine() bool
	// flags1 bit 5 versions 1-3, true if interpreter supports split screen, false otherwise
	CanSplitScreen() bool
	// flags1 bit 6 versions 1-3, true if interpreter defaults to variable-pitch font, false if defaults to fixed-pitch font
	IsDefaultVariablePitch() bool
	// flags1 bit 0 versions 5-8, true if interpreter supports colors, false otherwise
	CanColor() bool
	// flags1 bit 1 versions 6-8, true if interpreter supports pictures, false otherwise
	CanPicture() bool
	// flags1 bit 2 versions 4-8, true if interpreter supports bold fonts, false otherwise
	CanBold() bool
	// flags1 bit 3 versions 4-8, true if interpreter supports italic fonts, false otherwise
	CanItalic() bool
	// flags1 bit 4 versions 4-8, true if interpreter supports fixed-width, false otherwise
	CanFixedWidth() bool
	// flags1 bit 5 versions 6-8, true if interpreter supports sound effects, false otherwise
	CanSound() bool
	// flags1 bit 7 versions 4-8, true if interpreter supports timed keyboard input, false otherwise
	CanTimedInput() bool
	// true if interpreter supports UNDO opcodes, false otherwise
	CanUndo() bool
	// true if interpreter supports menus, false otherwise
	CanMenu() bool
	// true if interpreter supports mouse, false otherwise
	CanMouse() bool
	// true if interpreter supports transparency, false otherwise
	CanTransparency() bool
}

// Read a story file header
func (h *StoryFileHeader) Read(story StoryFile) (extHeader StoryFileExtendedHeader, err error) {
	story.Seek(0, 0)
	err = binary.Read(story, binary.BigEndian, h)
	if err == nil && h.HeaderExtensionAddress > 0 {
		frame, err := frame(story, h.HeaderExtensionAddress)
		if err == nil {
			extHeader := StoryFileExtendedHeader{}
			err = binary.Read(frame, binary.BigEndian, extHeader)
		}
	}
	return
}
