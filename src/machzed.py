from bytes import Bytes

class Machine:
    def __init__(self, story):
        self._memory = Memory(story)
        self._stack = []
        self.pc = 0

class Memory:
    def __init__(self, story):
        self._story = Bytes(story)

        self._header = Header(self._story[:0x40])
        # assert len(story) <= [0, 0x20000, 0x20000, 0x20000, 0x40000, 0x40000, 0x80000, 0x80000, 0x80000][self._version]

        static_start = story[0x0e]
        assert static_start > 0x40
        self._dynamic = story[:static_start]

        static_end = min(0xffff, len(story))
        assert static_start <= static_end
        self._static = story[static_start:static_end]

        high_start = min(high_offset, len(story))
        assert high_start >= static_start
        self._high = story[high_start:]

    def byte(self, offset):
        return self._story[offset]
    
    def word(self, offset):
        return self._story.word(offset*2)
    
    def routine(self, offset):
        if self._version <= 3:
            return self._high[offset * 2]
        if self._version in [4, 5]:
            return self._high[offset * 4]
        if self._version in [6, 7]:
            return self._high[offset * 4 + 8 * self.word[0x28]]
        return self._high[offset * 8]
    
    def string(self, offset):
        if self._version <= 3:
            return self._high[offset * 2]
        if self._version in [4, 5]:
            return self._high[offset * 4]
        if self._version in [6, 7]:
            return self._high[offset * 4 + 8 * self.word[0x2a]]
        return self._high[offset * 8]

class Header:
    def __init__(self, header):
        self._header = header
        self._version = int(header.byte(0x00))
        assert self.version_check(1, 2, 3, 4, 5, 6, 7, 8)
        self._flags1 = header.byte(0x01)
        self._high_offset = header.byte(0x04).unsigned()
        self._initial_pc = header.word(0x06).unsigned()
        self._dictionary_offset = header.word(0x08).unsigned()
        self._object_offset = header.word(0x0a).unsigned()
        self._global_offset = header.word(0x0c).unsigned()
        self._static_offset = header.word(0x0c).unsigned()
        self._flags2 = header.byte(0x10)
        self._flags2b = header.byte(0x11)
        self._abbreviation_offset = header.word(0x18).unsigned() # z2
        self._file_length = header.word(0x1a).unsigned() # z3
        self._file_checksum = header.word(0x1c).unsigned() # z3
        self._interpreter = header.byte(0x1e) # z4 # IR
        self._interpreter_version = header.byte(0x1f) # z4 # IR
        self._screen_lines = header.byte(0x20) # z4 # IR
        self._screen_line_chars = header.byte(0x21) # z4 # IR
        self._screen_width = header.word(0x22) # z4 # IR
        self._screen_height = header.word(0x24) # z4 # IR
        self._font_width = header.byte(0x26) # z5 # IR (reversed in x6)
        self._font_height = header.byte(0x27) # z5 # IR (reversed in x6)
        self._routine_offset = header.word(0x28).unsigned() # z6
        self._string_offset = header.word(0x2a).unsigned() # z6
        self._bg_color = header.byte(0x2c) # z5 # IR
        self._fg_color = header.byte(0x2d) # z5 # IR
        self._terminal_offset = header.word(0x2e).unsigned() # z5
        self._screen3_width = header.word(0x30).unsigned() # z6 # I
        self._revision = header.word(0x32).unsigned() # z1 # IR
        self._alphabet_offset = header.word(0x34).unsigned() # z5
        self._header_extension_offset = header.word(0x36).unsigned()
    
    def version_check(self, *versions):
        return self._version in versions

    def size_limit(self):
        if self.version_check(1, 2, 3):
            return 0x20000
        if self.version_check(4, 5):
            return 0x40000
        return 0x80000
    
    def is_status_line_timer(self): # otherwise score/turns
        if self.version_check(1, 2, 3):
            return self._flags1.is_bit(1)
        return False # is this right?
    
    def is_story_file_split(self):
        if self.version_check(1, 2, 3):
            return self._flags1.is_bit(2)
        return False
    
    def is_status_line_available(self):
        if self.version_check(1, 2, 3):
            return not self._flags1.is_bit(4) # IR
        return True
    
    def is_split_screen_available(self):
        if self.version_check(1, 2, 3):
            return self._flags1.is_bit(5) # IR
        return True
    
    def is_default_variable_pitch_font(self):
        if self.version_check(1, 2, 3):
            return self._flags1.is_bit(6) # IR
        return True
    
    def is_color_available(self):
        if self.version_check(5, 6, 7, 8):
            return self._flags1.is_bit(0) #IR
        return False
    
    def is_picture_display_available(self):
        if self.version_check(6, 7, 8):
            return self._flags1.is_bit(1) #IR
        return False
    
    def is_boldface_available(self):
        if self.version_check(4, 5, 6, 7, 8):
            return self._flags1.is_bit(2) #IR
        return False
    
    def is_italic_available(self):
        if self.version_check(4, 5, 6, 7, 8):
            return self._flags1.is_bit(3) #IR
        return False
    
    def is_monospace_available(self):
        if self.version_check(4, 5, 6, 7, 8):
            return self._flags1.is_bit(4) #IR
        return False
    
    def is_sound_available(self):
        if self.version_check(6, 7, 8):
            return self._flags1.is_bit(5) #IR
        return False
    
    def is_timed_input_available(self):
        if self.version_check(4, 5, 6, 7, 8):
            return self._flags1.is_bit(7) #IR
        return False

    def initial_pc(self):
        if self.version_check(1, 2, 3, 4, 5):
            return self._initial_pc
        return self.routine_offset(self._initial_pc)

    def is_transcripting_enabled(self):
        return self._flags2.is_bit(0) #DIR

    def is_force_fixed_pitch(self):
        if self.version_check(3, 4, 5, 6, 7, 8):
            return self._flags2.is_bit(1) #DR
        return False
    
    def is_redraw_request(self):
        if self.version_check(6, 7, 8):
            return self._flags2.is_bit(2) #DI
        return False
    
    def is_picture_request(self):
        if self.version_check(5, 6, 7, 8):
            return self._flags2.is_bit(3) #IR
        return False
    
    def is_undo_request(self):
        if self.version_check(5, 6, 7, 8):
            return self._flags2.is_bit(4) #IR
        return False
    
    def is_mouse_request(self):
        if self.version_check(5, 6, 7, 8):
            return self._flags2.is_bit(5) #IR
        return False
    
    def is_color_request(self):
        if self.version_check(5, 6, 7, 8):
            return self._flags2.is_bit(6) #
        return False
    
    def is_sound_request(self):
        if self.version_check(5, 6, 7, 8):
            return self._flags2.is_bit(7) #IR
        return False
    
    def is_menu_request(self):
        if self.version_check(6, 7, 8):
            return self._flags2b.is_bit(0) #IR
        return False
    
    def string_offset(self, offset):
        if self._version in [1, 2, 3]:
            return offset * 2 + self._high_offset
        if self._version in [4, 5]:
            return offset * 4 + self._high_offset
        if self._version in [6, 7]:
            return offset * 4 + 8 * self._string_offset + self._high_offset
        return offset * 8 + self._high_offset

    def routine_offset(self, offset):
        if self._version in [1, 2, 3]:
            return offset * 2 + self._high_offset
        if self._version in [4, 5]:
            return offset * 4 + self._high_offset
        if self._version in [6, 7]:
            return offset * 4 + 8 * self._routine_offset + self._high_offset
        return offset * 8 + self._high_offset


