#include <msp430.h>
#include <stdlib.h>
#include "radio.h"
#include "clock.h"
#include "utils.h"
#include "adc.h"

/* SENDER */


const long CLOCK_FREQUENCY = 8000000;

char should_send_data = 0;


void send_data() {
    should_send_data = 0;

    int data1 = get_adc_value(ADC_CHANNEL_0);
    int data2 = get_adc_value(ADC_CHANNEL_1);

    send_radio_int_data(data1);
    send_radio_int_data(data2);
}


int main(void) {
    WDTCTL = WDTPW + WDTHOLD;
    OUTPUT(P1DIR, BIT0);
    UNSET(P1OUT, BIT0);

    setup_clock(CLOCK_FREQUENCY);
    setup_timer(CLOCK_FREQUENCY, 2500);
    setup_radio_transmit_mode();

    __bis_SR_register(GIE);

    while(1) {
        if (should_send_data) {
            send_data();
        }
    }
}


#pragma vector=TIMER0_A0_VECTOR
__interrupt void TIMER_A0_ISR (void) {
    should_send_data = 1;
}


#pragma vector=PORT2_VECTOR
__interrupt void Port_2(void) {
    clear_IFG_interrupt();
    TOGGGLE(P1OUT, BIT0);
}
