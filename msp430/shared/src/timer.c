#include <msp430.h>
#include <timer.h>
#include <utils.h>
#include <assert.h>

/*
 * @param UCSCTL2_value = clock_frequency (Hz) / 32768 Hz - 1
 * @param TA0CCR0_value = clock_frequency (Hz) * interrupt_frequency(s)
 * */
void setup_timer(int UCSCTL2_value, int TA0CCR0_value) {
    OVERWRITE(UCSCTL3, SELREF__REFOCLK); // setp 1

    SET(UCSCTL4, SELA__REFOCLK); // step 2
    CLEAR(UCSCTL0); // step 3

    do {
        UNSET(UCSCTL7, XT2OFFG + XT1LFOFFG + DCOFFG); // step 4
        UNSET(SFRIFG1, OFIFG); // step 5
    } while (SFRIFG1 & OFIFG); // step 6

    __bis_SR_register(SCG0);

    OVERWRITE(UCSCTL1, DCORSEL_5); // step 7 - TODO which DCORSEL_X to choose?
                                   // From datasheet : DCOCORSEL_6 with DCO and MOD at 0,
                                   // range is between 4.6MHz and 10.7MHz

    OVERWRITE(UCSCTL2, FLLD_0 + UCSCTL2_value); // step 8 - TODO not sure if right value
                            // Base frequency : 32768Hz
                            // 8 000 000 / 32768 - 1 = N ~= 243

    __bic_SR_register(SCG0);
    __delay_cycles(250000);

    // OPTIONAL
    // OUTPUT(P7DIR, BIT7); // step 9
    // SET(P7SEL, BIT7); // step 9

    OVERWRITE(TA0CCTL0, CCIE); // step 10

    OVERWRITE(TA0CCR0, TA0CCR0_value); // step 11 - fréquence (Hz) * temps (s)
                              // = 8 000 000 * 0.0002 = 1600

    OVERWRITE(TA0CTL, TASSEL_1 + MC_1 + ID_0); // step 12
}
