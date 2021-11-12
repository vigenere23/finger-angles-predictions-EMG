#include <msp430.h>
#include <stdlib.h>
#include "clock.h"
#include "utils.h"
#include "uart.h"
#include "radio.h"

/* RECEIVER */


int should_receive_data = 0;
char receive_buffer[RADIO_PACKET_LENGTH];

void receive_data() {
    should_receive_data = 0;

    receive_radio_data(receive_buffer);

    int i;
    for (i = 0; i < RADIO_PACKET_LENGTH; i++) {
        send_uart_data_byte(receive_buffer[i]);
    }
}

int main(void)
{
    const long CLOCK_FREQUENCY = 8000000;
    const UARTConfig UART_CONFIG = {
        .sync_byte = '\n',
        .channels = 2,
        .data_length = 128,
        .message_length = 2,
        .check_byte = 0xFF
    };

    WDTCTL = WDTPW | WDTHOLD;

    OUTPUT(P4DIR, BIT7);

    setup_clock(CLOCK_FREQUENCY);
    setup_uart(&UART_CONFIG);
    setup_receive_mode();

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
}
