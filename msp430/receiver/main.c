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

    unsigned char i;
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

    OUTPUT(P1DIR, BIT0);
    UNSET(P1OUT, BIT0);

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
    should_receive_data = 1;
    TOGGGLE(P1OUT, BIT0);
    clear_IFG_interrupt();
}

#pragma vector=USCI_A1_VECTOR
__interrupt void USCI_A1_ISR(void) {
    switch(__even_in_range(UCA1IV,4)) {
        case 0:break;
        case 2:
            // TOGGGLE(P1OUT, BIT0);
            break;
        case 4:break;
        default:
        break;
    }
}
