/*
 * ds18b20.c
 *
 *  Created on: Dec 13, 2012
 *      Author: Roman Rader
 */

#include <msp430.h>
#include "OneWire/onewire.h"
#include "OneWire/delay.h"

//Port 1
onewire_t init_1wire(int pin) {
	onewire_t ow; 			// 1Wire ds18b20 init
	ow.port_out = &P1OUT;
	ow.port_in = &P1IN;
	ow.port_ren = &P1REN;
	ow.port_dir = &P1DIR;
	ow.pin = pin;
	return ow;
}

uint8_t* ds18b20_read(onewire_t *ow) {
	uint8_t scratchpad[8];

	onewire_reset(ow);
	onewire_write_byte(ow, 0xcc); // skip ROM command
	onewire_write_byte(ow, 0x44); // convert T command
	onewire_line_high(ow);
	DELAY_MS(800); // at least 750 ms for the default 12-bit resolution
	onewire_reset(ow);
	onewire_write_byte(ow, 0xcc); // skip ROM command
	onewire_write_byte(ow, 0xbe); // read scratchpad command
	int i;
	for (i = 0; i < 9; i++) scratchpad[i] = onewire_read_byte(ow);
	onewire_reset(ow);

	return scratchpad;
}
