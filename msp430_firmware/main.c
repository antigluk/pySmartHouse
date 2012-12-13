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
#include "ds18b20.h"

#define TEMP0 BIT7

#define CHECK_BIT(var,pos) ((var) & (1<<(pos)))

int main(void)
{
  WDTCTL = WDTPW + WDTHOLD; // Stop WDT
  BCSCTL1 = CALBC1_8MHZ; 	//Set DCO to 8Mhz
  DCOCTL = CALDCO_8MHZ; 	//Set DCO to 8Mhz
  P1DIR = 0x00;
  P2DIR = 0x00;
  P3DIR = 0x00;

  onewire_t temp = init_1wire(TEMP0);

  uart_init();
  __enable_interrupt();
  temp_init();

  long Temp = 0;
  for(;;) {
	uart_getc();
	Temp = temp_measure();

	uint8_t *scratchpad;

	scratchpad = ds18b20_read(&temp);
//	int D1 = CHECK_BIT(P1IN, BIT7);
//	uart_printf("T1\t%i;P1\t%i;P2\t%i;P3\t%i\n\r", Temp, P1IN, P2IN, P3IN);
	uart_printf("T1\t%i;ds18b20:%i%i\n\r", Temp, scratchpad[0], scratchpad[1]);
  }
  return 0;
}
