#ifndef INCLUDE_ADC_H_
#define INCLUDE_ADC_H_


#include <msp430.h>

#define ADC_CHANNEL_0 ADC12MEM0
#define ADC_CHANNEL_1 ADC12MEM1

void setup_adc();

int get_adc_value(unsigned int channel);


#endif /* INCLUDE_ADC_H_ */
