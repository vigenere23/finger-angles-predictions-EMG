#ifndef UTILS_H_
#define UTILS_H_


#define INPUT(dir, bit) dir &= ~(bit)
#define OUTPUT(dir, bit) dir |= bit
#define SET(pin, bit) pin |= bit
#define UNSET(pin, bit) pin &= ~(bit)
#define OVERWRITE(pin, bit) pin = bit
#define CLEAR(pin) pin = 0
#define TOGGGLE(pin, bit) pin ^= bit
#define IS_SET(pin, bit) !(pin & (bit))


#endif /* UTILS_H_ */
