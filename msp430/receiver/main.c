#include <msp430.h>
#include "clock.h"
#include "utils.h"

/* RECEIVER */

int main(void)
{
    const long CLOCK_FREQUENCY = 8000000;

    WDTCTL = WDTPW | WDTHOLD;

    OUTPUT(P1DIR, BIT0);

    setup_clock(CLOCK_FREQUENCY);
    setup_timer(CLOCK_FREQUENCY, 500);

    __bis_SR_register(LPM0_bits + GIE);
    __no_operation();

    return 0;
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void TIMER_A0_ISR (void) {
    TOGGGLE(P1OUT, BIT0);
}
