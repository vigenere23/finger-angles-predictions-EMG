#include <msp430.h>
#include "utils.h"


void setup_adc() {
    INPUT(P6DIR, BIT0); // step 1
    SET(P6SEL, BIT0); // step 2
    UNSET(REFCTL0, REFMSTR); // step 3
    OVERWRITE(ADC12CTL0, ADC12ON + ADC12REFON + /*ADC12SHT10 +*/ ADC12REF2_5V); // step 4
                                                                                // TODO ADC12SHT00 value??
    OVERWRITE(ADC12CTL1, ADC12SHP); // step 5
    OVERWRITE(ADC12MCTL0, ADC12SREF0); // step 6

    int i;
    for (i=0; i < 0x30; i++);

    SET(ADC12CTL0, ADC12ENC); // step 7
}

int get_adc_value() {
    SET(ADC12CTL0, ADC12SC); // start conversion sampling
    while (!(ADC12IFG & BIT0)); // wait for conversion to complete

    return ADC12MEM0;
}
