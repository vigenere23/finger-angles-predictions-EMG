#include <msp430.h>
#include "utils.h"
#include "adc.h"


void setup_adc() {
    INPUT(P6DIR, BIT0);
    SET(P6SEL, BIT0);
    UNSET(REFCTL0, REFMSTR);
    OVERWRITE(ADC12CTL0, ADC12ON + ADC12REFON + ADC12SHT0_4 + ADC12REF2_5V + ADC12MSC);
    OVERWRITE(ADC12CTL1, ADC12SHP + ADC12CONSEQ_1);
    // OVERWRITE(ADC12MCTL0, ADC12SREF0);
    OVERWRITE(ADC12MCTL0, ADC12INCH_0);
    OVERWRITE(ADC12MCTL1, ADC12INCH_1);

    __delay_cycles(100000);

    SET(ADC12CTL0, ADC12ENC); // step 7
}

int get_adc_value(unsigned int channel) {
    SET(ADC12CTL0, ADC12SC); // start conversion sampling
    while (!(ADC12IFG & BIT0)); // wait for conversion to complete

    return channel;
}
