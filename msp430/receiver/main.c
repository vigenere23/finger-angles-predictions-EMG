#include <msp430.h>
#include "clock.h"
#include "utils.h"
#include "uart.h"
#include "radio.h"

/* RECEIVER */


const long CLOCK_FREQUENCY = 8000000;
const UARTConfig UART_CONFIG = {
    .sync_byte = '\n',
    .channels = 2,
    .data_length = 128,
    .message_length = 2,
    .check_byte = 0xFF
};


char receive_buffer[RADIO_PACKET_LENGTH];
unsigned char receive_buffer_index = 0;
int should_receive_data = 0;


void receive_data() {
    should_receive_data = 0;

    receive_radio_data(receive_buffer);

    for (receive_buffer_index = 0; receive_buffer_index < RADIO_PACKET_LENGTH; receive_buffer_index++) {
        send_uart_data_byte(receive_buffer[receive_buffer_index]);
    }
}


int main(void) {
    WDTCTL = WDTPW | WDTHOLD;

    OUTPUT(P1DIR, BIT0);
    UNSET(P1OUT, BIT0);

    setup_clock(CLOCK_FREQUENCY);
    setup_uart(&UART_CONFIG);
    setup_radio_receive_mode();

    __bis_SR_register(GIE);

    while (1) {
        if (should_receive_data) {
            receive_data();
        }
    }
}


#pragma vector=PORT2_VECTOR
__interrupt void Port_2(void) {
    clear_IFG_interrupt();
    should_receive_data = 1;
    TOGGGLE(P1OUT, BIT0);
}
