#include <msp430.h>
#include <stdlib.h>
#include "radio.h"
#include "clock.h"
#include "utils.h"
#include "adc.h"

/* SENDER */


int should_send_data = 0;

void send_data() {
    should_send_data = 0;

    int data1 = get_adc_value(ADC_CHANNEL_0);
    int data2 = get_adc_value(ADC_CHANNEL_1);

    send_radio_int_data(data1);
    send_radio_int_data(data2);
}

int main(void)
{
    const long CLOCK_FREQUENCY = 8000000;

    WDTCTL = WDTPW | WDTHOLD;

    OUTPUT(P4DIR, BIT7);

    setup_adc();
    setup_clock(CLOCK_FREQUENCY);
    setup_timer(CLOCK_FREQUENCY, 2000);

    __bis_SR_register(GIE);

    while (1) {
        if (should_send_data) {
            send_data();
        }
    }
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void TIMER_A0_ISR (void) {
    clear_IFG_interrupt();
    should_send_data = 1;
}
