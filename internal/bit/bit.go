package bit

// IsSet returns whether a bit 'pos' is set in 'bitfield'
func IsSet(bitfield byte, pos uint) bool {
	return bitfield&(1<<pos) > 0
}
