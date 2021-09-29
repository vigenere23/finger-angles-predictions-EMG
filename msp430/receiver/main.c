#include <msp430.h>
#include "timer.h"
#include "utils.h"

/* RECEIVER */

/**
 * main.c
 */
int main(void)
{
    WDTCTL = WDTPW | WDTHOLD;   // stop watchdog timer

    OUTPUT(P1DIR, BIT0);

    setup_timer(243, 1600); // start timer at 8MHz clock and 200us interrupt

    __bis_SR_register(LPM0_bits + GIE);
    __no_operation();

    return 0;
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void TIMER_A0_ISR (void) {
    TOGGGLE(P1OUT, BIT0); // step 14
}
