/*
 * ds18b20.h
 *
 *  Created on: Dec 13, 2012
 *      Author: roma
 */

#ifndef DS18B20_H_
#define DS18B20_H_

#include "OneWire/onewire.h"

onewire_t init_1wire(int pin);
uint8_t* ds18b20_read(onewire_t *ow);

#endif /* DS18B20_H_ */
