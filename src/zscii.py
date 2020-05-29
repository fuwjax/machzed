class Zscii:
    def __init__(self, header, bytes):
        self._bytes = bytes
        self._header = header
        self._zscii = [x for x in range(256)]
        self._zscii[0] = 'NIL'
        self._zscii[8] = 'DEL'
        self._zscii[9] = '\t'
        self._zscii[11] = ' '
        self._zscii[13] = '\n'
        self._zscii[27] = 'ESC'
        self._zscii[129:133] = ['CUP','CDN','CLT','CRT']
        self._zscii[133:144] = ['F01','F02','F03','F04','F05','F06','F07','F08','F09','F10','F11','F12']
        self._zscii[145:155] = ['NO0','NO1','NO2','NO3','NO4','NO5','NO6','NO7','NO8','NO9']
        self._zscii[155:252] = "äöüÄÖÜß»«ëïÿËÏáéíóúýÁÉÍÓÚÝàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛåÅøØãñõÃÑÕæÆçÇþðÞÐ£œŒ¡¿"[:]
        self._zscii[252:255] = ['MNU','DCK','SCK']
        if header.version_check(5,6,7,8) and int(header._unicode_translation_offset) > 0:
            count = int(bytes[int(header._unicode_translation_offset)])
            for i in range(count):
                self._zscii[155 + i] = int(bytes.address(int(header._unicode_translation_offset) + 1 + i * 2))
        self._alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \n0123456789.,!?_#'\"/\\-:()".encode('ascii')
        if header.version_check(1):
            self._alphabet[52:] = " 0123456789.,!?_#'\"/\\<-:()".encode('ascii')
        if int(header._alphabet_offset) > 0:
            temp = bytes[int(header._alphabet_offset): int(header._alphabet_offset) + 78].bytes()
            self._alphabet = [temp[:26], temp[26:52], temp[52:]]
    def zstr(self, offset):
        zchars = self._bytes.zchars(offset)
        alpha = 0
        lock = False
        abbr = None
        pair = None
        s = ''
        for zch in zchars:
            if pair is not None:
                pair.append(zch)
                if len(pair) == 2:
                    s += chr(self._zscii[pair[0] << 5 + pair[1]])
                    pair = None
            elif abbr is not None:
                s += self.zstr(int(self._header._abbreviation_offset) + abbr * 32 + zch)
                abbr = None
            elif zch == 0:
                s += ' '
            elif zch == 1:
                abbr = 0
            elif zch in [2,3]:
                if self._header.version_check(1,2):
                    alpha = (alpha + zch - 1 ) % 3
                else:
                    abbr = zch - 1
            elif zch in [4,5]:
                alpha = (alpha + zch ) % 3
                if self._header.version_check(1,2):
                    lock = True
            elif zch == 6 and alpha == 2:
                pair = []
            else:
                s += chr(self._zscii[self._alphabet[alpha * 26 + zch - 6]])
            if not lock:
                alpha = 0
        return s

