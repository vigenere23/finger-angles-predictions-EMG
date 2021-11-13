#include <msp430.h>
#include <stdlib.h>
#include "nRF.h"
#include "radio.h"
#include "clock.h"
#include "utils.h"
#include "adc.h"

/* SENDER */

char should_send_data = 0;
char TX_data_buffer[32];
unsigned char i;

int main(void) {
    WDTCTL = WDTPW + WDTHOLD;
    OUTPUT(P1DIR, BIT0);
    UNSET(P1OUT, BIT0);

    setup_clock(8000000);
    setup_timer(8000000, 2000);
    setup_transmit_mode();

    __bis_SR_register(GIE);

    while(1) {
        if (should_send_data) {
            should_send_data = 0;

            for(i = 0; i < 32; i++)
                TX_data_buffer[i] = 0;

            // Message to be sent = 'Hello!'
            TX_data_buffer[0] = 'H';
            TX_data_buffer[1] = 'e';
            TX_data_buffer[2] = 'l';
            TX_data_buffer[3] = 'l';
            TX_data_buffer[4] = 'o';
            TX_data_buffer[5] = '!';
            TX_data_buffer[6] = '\n';
            send_radio_data(TX_data_buffer);
        }
    }
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void TIMER_A0_ISR (void) {
    should_send_data = 1;
}

#pragma vector=PORT2_VECTOR
__interrupt void Port_2(void)
{
    clear_IFG_interrupt();
    TOGGGLE(P1OUT, BIT0);
}
