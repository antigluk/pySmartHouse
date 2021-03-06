/*
 * temp.c
 *
 *  Created on: Dec 2, 2012
 *      Author: roma
 */
#include <msp430g2553.h>
#include "temp_internal.h"

long temp;
long IntDegF;
long IntDegC;


void temp_init(void) {
	  ADC10CTL1 = INCH_10 + ADC10DIV_3;         // Temp Sensor ADC10CLK/4
	  ADC10CTL0 = SREF_1 + ADC10SHT_3 + REFON + ADC10ON + ADC10IE;
	  __enable_interrupt();                     // Enable interrupts.
	  TACCR0 = 30;                              // Delay to allow Ref to settle
	  TACCTL0 |= CCIE;                          // Compare-mode interrupt.
	  TACTL = TASSEL_2 | MC_1;                  // TACLK = SMCLK, Up mode.
	  LPM0;                                     // Wait for delay.
	  TACCTL0 &= ~CCIE;                         // Disable timer Interrupt
}

int temp_measure(void) {
    ADC10CTL0 |= ENC + ADC10SC;             // Sampling and conversion start
    __bis_SR_register(CPUOFF + GIE);        // LPM0 with interrupts enabled

    // oC = ((A10/1024)*1500mV)-986mV)*1/3.55mV = A10*423/1024 - 278
    temp = ADC10MEM;
    IntDegC = ((temp - 673) * 423) / 1024 - 4;
    return IntDegC;
}



// ADC10 interrupt service routine
#pragma vector=ADC10_VECTOR
__interrupt void ADC10_ISR (void)
{
  __bic_SR_register_on_exit(CPUOFF);        // Clear CPUOFF bit from 0(SR)
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void ta0_isr(void)
{
  TACTL = 0;
  LPM0_EXIT;                                // Exit LPM0 on return
}
