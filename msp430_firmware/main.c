//******************************************************************************
//  MSP430G2x33/G2x53 Demo - ADC10, Sample A10 Temp and Convert to oC and oF
//
//  Description: A single sample is made on A10 with reference to internal
//  1.5V Vref. Software sets ADC10SC to start sample and conversion - ADC10SC
//  automatically cleared at EOC. ADC10 internal oscillator/4 times sample
//  (64x) and conversion. In Mainloop MSP430 waits in LPM0 to save power until
//  ADC10 conversion complete, ADC10_ISR will force exit from any LPMx in
//  Mainloop on reti. Temperaure in oC stored in IntDegC, oF in IntDegF.
//  Uncalibrated temperature measured from device to device will vary with
//  slope and offset - please see datasheet.
//  ACLK = n/a, MCLK = SMCLK = default DCO ~1.2MHz, ADC10CLK = ADC10OSC/4
//
//                MSP430G2x33/G2x53
//             -----------------
//         /|\|              XIN|-
//          | |                 |
//          --|RST          XOUT|-
//            |                 |
//            |A10              |
//
//  D. Dang
//  Texas Instruments Inc.
//  December 2010
//   Built with CCS Version 4.2.0 and IAR Embedded Workbench Version: 5.10
//******************************************************************************
#include  "msp430g2553.h"
#include "printf.h"
#include "uart.h"
#include "temp_internal.h"
#include "OneWire/onewire.h"
#include "OneWire/delay.h"

#define TEMP0 BIT7

#define CHECK_BIT(var,pos) ((var) & (1<<(pos)))

int main(void)
{
  WDTCTL = WDTPW + WDTHOLD;                 // Stop WDT
  BCSCTL1 = CALBC1_8MHZ; 				//Set DCO to 8Mhz
  DCOCTL = CALDCO_8MHZ; 				//Set DCO to 8Mhz
  P1DIR = 0x00;
  P2DIR = 0x00;
  P3DIR = 0x00;

  onewire_t ow;
  ow.port_out = &P1OUT;
  ow.port_in = &P1IN;
  ow.port_ren = &P1REN;
  ow.port_dir = &P1DIR;
  ow.pin = TEMP0;
  uint8_t scratchpad[9];

  uart_init();
  __enable_interrupt();				//Interrupts Enabled
  temp_init();

  long Temp = 0;
  for(;;) {
	uart_getc();
	Temp = temp_measure();

	onewire_reset(&ow);
	onewire_write_byte(&ow, 0xcc); // skip ROM command
	onewire_write_byte(&ow, 0x44); // convert T command
	onewire_line_high(&ow);
	DELAY_MS(800); // at least 750 ms for the default 12-bit resolution
	onewire_reset(&ow);
	onewire_write_byte(&ow, 0xcc); // skip ROM command
	onewire_write_byte(&ow, 0xbe); // read scratchpad command
	int i;
	for (i = 0; i < 9; i++) scratchpad[i] = onewire_read_byte(&ow);



//	int D1 = CHECK_BIT(P1IN, BIT7);
//	uart_printf("T1\t%i;P1\t%i;P2\t%i;P3\t%i\n\r", Temp, P1IN, P2IN, P3IN);
	uart_printf("T1\t%i\n\r", Temp);
  }
  return 0;
}
