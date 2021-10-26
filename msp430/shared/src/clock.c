#include <msp430.h>
#include "clock.h"
#include "utils.h"


void setup_clock(long clock_freq) {
    OVERWRITE(UCSCTL3, SELREF__REFOCLK); // step 1

    SET(UCSCTL4, SELA__REFOCLK); // step 2
    CLEAR(UCSCTL0); // step 3

    do {
        UNSET(UCSCTL7, XT2OFFG + XT1LFOFFG + DCOFFG); // step 4
        UNSET(SFRIFG1, OFIFG); // step 5
    } while (SFRIFG1 & OFIFG); // step 6

    __bis_SR_register(SCG0);

    OVERWRITE(UCSCTL1, DCORSEL_5); // step 7
                                   // From datasheet : DCOCORSEL_6 with DCO and MOD at 0,
                                   // range is between 4.6MHz and 10.7MHz

    OVERWRITE(UCSCTL2, FLLD_0 + clock_freq / 32768 - 1); // step 8
                            // Base frequency : 32768Hz
                            // 8 000 000 / 32768 - 1 = N ~= 243

    __bic_SR_register(SCG0);
    __delay_cycles(250000);
}


void setup_timer(long clock_freq, int timer_freq) {
    OVERWRITE(TA0CCTL0, CCIE); // step 10

    OVERWRITE(TA0CCR0, clock_freq / timer_freq); // step 11 - fréquence (Hz) * temps (s)
                              // = 8 000 000 * 0.0002 = 1600
                              // = clock_freq / interrupt_freq

    OVERWRITE(TA0CTL, TASSEL_2 + MC_1 + ID_0); // step 12
}
