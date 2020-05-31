from bytes import Bytes
from header import Header
from zscii import Zscii

with open("docs/test/czech_0_8/czech.z5", "rb") as story_file:
    bytes = Bytes(story_file.read())
print("Size: "+str(len(bytes)))
header = Header(bytes)

print(header)

print(bytes.zchars(header.string_offset(0)))

zscii = Zscii(header, bytes)
print(zscii.zstr(header.string_offset(0)))
