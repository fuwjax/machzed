from bytes import ON, OFF, ZERO

class Header:
    def __init__(self, header):
        self._header = header
        self._version = header.byte(0x00)
        assert self.version_check(1, 2, 3, 4, 5, 6, 7, 8)
        self._has_timer_status_line = header.bit(0x01, 1) if self.version_check(1, 2, 3) else OFF
        self._has_split_story_file = header.bit(0x01, 2) if self.version_check(1, 2, 3) else OFF
        self._tandy_bit = header.bit(0x01, 3) if self.version_check(3) else OFF
        self._has_no_status_line = header.bit(0x01, 4) if self.version_check(1, 2, 3) else OFF
        self._can_split_screen = header.bit(0x01, 5) if self.version_check(1, 2, 3) else ON
        self._has_default_variable_pitch_font = header.bit(0x01, 6) if self.version_check(1, 2, 3) else ON
        self._has_colors = header.bit(0x01, 0) if self.version_check(5, 6, 7, 8) else OFF
        self._has_pictures = header.bit(0x01, 1) if self.version_check(6, 7, 8) else OFF
        self._has_boldface = header.bit(0x01, 2) if self.version_check(4, 5, 6, 7, 8) else OFF
        self._has_italics = header.bit(0x01, 3) if self.version_check(4, 5, 6, 7, 8) else OFF
        self._has_monospace = header.bit(0x01, 4) if self.version_check(4, 5, 6, 7, 8) else OFF
        self._has_sound = header.bit(0x01, 5) if self.version_check(6, 7, 8) else OFF
        self._has_timed_input = header.bit(0x01, 7) if self.version_check(4, 5, 6, 7, 8) else OFF
        self._release = header.address(0x02)
        self._high_offset = header.address(0x04)
        self._initial_pc = header.address(0x06) if self.version_check(1, 2, 3, 4, 5) else self.routine_offset(int(header.address(0x06)))
        self._dictionary_offset = header.address(0x08)
        self._object_offset = header.address(0x0a)
        self._global_offset = header.address(0x0c)
        self._static_offset = header.address(0x0c)
        self._is_transcribing_on = header.bit(0x10, 0)
        self._force_monospace = header.bit(0x10, 1) if self.version_check(3, 4, 5, 6, 7, 8) else ON
        self._request_redraw = header.bit(0x10, 2) if self.version_check(6, 7, 8) else OFF
        self._uses_pictures = header.bit(0x10, 3) if self.version_check(5, 6, 7, 8) else OFF
        self._uses_undo = header.bit(0x10, 4) if self.version_check(5, 6, 7, 8) else OFF
        self._uses_mouse = header.bit(0x10, 5) if self.version_check(5, 6, 7, 8) else OFF
        self._uses_colors = header.bit(0x10, 6) if self.version_check(5, 6, 7, 8) else OFF
        self._uses_sounds = header.bit(0x10, 7) if self.version_check(5, 6, 7, 8) else OFF
        self._uses_menus = header.bit(0x11, 0) if self.version_check(6, 7, 8) else OFF
        self._transcription_error = header.bit(0x11, 2) # technically unknown
        self._serial_code = header[0x12:0x18].bytes().decode('ascii')
        self._abbreviation_offset = header.address(0x18) # z2
        self._file_length = int(header.address(0x1a)) * self.length_multiplier() # z3
        self._file_checksum = header.address(0x1c) # z3
        self._file_size_limit = 0x10000 * self.length_multiplier()
        self._interpreter = header.byte(0x1e) # z4 # IR
        self._interpreter_version = header.byte(0x1f) # z4 # IR
        self._screen_lines = header.byte(0x20) # z4 # IR
        self._screen_line_chars = header.byte(0x21) # z4 # IR
        self._screen_width = header.address(0x22) # z4 # IR
        self._screen_height = header.address(0x24) # z4 # IR
        self._font_width = header.byte(0x26 if self.version_check(1, 2, 3, 4, 5) else 0x27) # z5 # IR (reversed in x6)
        self._font_height = header.byte(0x27 if self.version_check(1, 2, 3, 4, 5) else 0x26) # z5 # IR (reversed in x6)
        self._routine_offset = header.address(0x28) # z6
        self._string_offset = header.address(0x2a) # z6
        self._bg_color = header.byte(0x2c) # z5 # IR
        self._fg_color = header.byte(0x2d) # z5 # IR
        self._terminal_offset = header.address(0x2e) # z5
        self._screen3_width = header.address(0x30) # z6 # I
        self._revision = header.address(0x32) # z1 # IR
        self._alphabet_offset = header.address(0x34) # z5
        self._header_extension_offset = header.address(0x36)
        self._user = header[0x38: 0x40]
        self._compiler_version = header[0x3C:0x40].bytes().decode('ascii')
        if int(self._header_extension_offset) > 0:
            offset = int(self._header_extension_offset)
            words = int(header.address(offset))
            self._mouse_x = header.address(offset + 2) if words >= 1 else ZERO
            self._mouse_y = header.address(offset + 4) if words >= 2 else ZERO
            self._unicode_translation_offset = header.address(offset + 6) if words >= 3 else ZERO
            self._uses_transparency = header.bit(offset + 8, 0) if words >= 4 else OFF
            self._true_fg_color = header.bit(offset + 10, 0) if words >= 5 else self._fg_color
            self._true_bg_color = header.bit(offset + 12, 0) if words >= 6 else self._bg_color
        else:
            self._mouse_x = ZERO
            self._mouse_y = ZERO
            self._unicode_translation_offset = ZERO
            self._uses_transparency = OFF
            self._true_fg_color = self._fg_color
            self._true_bg_color = self._bg_color

    def version_check(self, *versions):
        return int(self._version) in versions
    
    def length_multiplier(self):
        if self.version_check(1, 2, 3):
            return 2
        if self.version_check(4, 5):
            return 4
        return 8

    def string_offset(self, offset):
        if self.version_check(1, 2, 3):
            return offset * 2 + int(self._high_offset)
        if self.version_check(4, 5):
            return offset * 4 + int(self._high_offset)
        if self.version_check(6, 7):
            return offset * 4 + 8 * self._string_offset + int(self._high_offset)
        return offset * 8 + int(self._high_offset)

    def routine_offset(self, offset):
        if self.version_check(1, 2, 3):
            return offset * 2 + int(self._high_offset)
        if self.version_check(4, 5):
            return offset * 4 + int(self._high_offset)
        if self.version_check(6, 7):
            return offset * 4 + 8 * self._routine_offset + int(self._high_offset)
        return offset * 8 + int(self._high_offset)

    def __str__(self):
        return """\
version: {_version}
release: {_release}
serial number: {_serial_code}
initial PC: {_initial_pc}
file length: {_file_length}
file checksum: {_file_checksum}
file limit: {_file_size_limit}
interpreter: {_interpreter}
interpreter version: {_interpreter_version}
compiler version: {_compiler_version}
Standard revision: {_revision}
Offsets:
  high: {_high_offset}
  dictionary: {_dictionary_offset}
  object: {_object_offset}
  global: {_global_offset}
  static: {_static_offset}
  abbreviation: {_abbreviation_offset}
  terminal: {_terminal_offset}
  alphabet: {_alphabet_offset}
  header extension: {_header_extension_offset}
  routine: {_routine_offset}
  string: {_string_offset}
  unicode translation: {_unicode_translation_offset}
Flags:
  Status line type: False=score/turns, True=hours:mins: {_has_timer_status_line}
  Story file split across two discs? {_has_split_story_file}
  The legendary "Tandy" bit: {_tandy_bit}
  Status line not available? {_has_no_status_line}
  Screen-splitting available? {_can_split_screen}
  Is a variable-pitch font the default? {_has_default_variable_pitch_font}
  Colours available? {_has_colors}
  Picture displaying available? {_has_pictures}
  Boldface available? {_has_boldface}
  Italic available? {_has_italics}
  Fixed-space style available? {_has_monospace}
  Sound effects available? {_has_sound}
  Timed keyboard input available? {_has_timed_input}
  Set when transcripting is on: {_is_transcribing_on}
  Game sets to force printing in fixed-pitch font: {_force_monospace}
  Int sets to request screen redraw: game clears when it complies with this: {_request_redraw}
  If set, game wants to use pictures: {_uses_pictures}
  If set, game wants to use the UNDO opcodes: {_uses_undo}
  If set, game wants to use a mouse: {_uses_mouse}
  If set, game wants to use colors: {_uses_colors}
  If set, game wants to use sound effects: {_uses_sounds}
  If set, game wants to use menus: {_uses_menus}
  If set, game wants to use transparency: {_uses_transparency}
Screen:
  Screen height (lines): 255 means "infinite": {_screen_lines}
  Screen width (characters): {_screen_line_chars}
  Screen width in units: {_screen_width}
  Screen height in units: {_screen_height}
  Font width in units (defined as width of a '0'): {_font_width}
  Font height in units: {_font_height}
  Default background color: {_bg_color}
  Default foreground color: {_fg_color}
  True default background color: {_true_bg_color}
  True default foreground color: {_true_fg_color}
  Total width in pixels of text sent to output stream 3: {_screen3_width}
  X-coordinate of mouse after a click: {_mouse_x}
  Y-coordinate of mouse after a click: {_mouse_y}
        """.format(**self.__dict__)
