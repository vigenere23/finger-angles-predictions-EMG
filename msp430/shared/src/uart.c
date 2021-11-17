#include <msp430.h>
#include "uart.h"
#include "utils.h"


const UARTConfig* CONFIG;
int data_counter = 0;


void send_byte(char byte) {
    while(!(UCA1IFG & UCTXIFG)); // Wait for TX buffer to be ready for new data
    UCA1TXBUF = byte;
}


void send_uart_prefix() {
    send_byte(CONFIG->sync_byte);
    send_byte(CONFIG->channels);
    send_byte(CONFIG->message_length);
    send_byte(CONFIG->data_length);
}

void send_uart_suffix() {
    send_byte(CONFIG->check_byte);
}


void setup_uart(const UARTConfig* config) {
    CONFIG = config;

    SET(P4SEL, BIT4 + BIT5); // step 1
    SET(UCA1CTL1, UCSWRST); // step 2
    SET(UCA1CTL1, UCSSEL__SMCLK); // step 3

    // SET(UCA1CTL0, UCPEN); // enable odd parity

    // baud rate = 8000000 / (UCA1BR1 * 256 + UCA1BR0)
    // <=> UCA1BR1 * 256 + UCA1BR0 = 8 000 000 / 115200 = 69.4444
    OVERWRITE(UCA1BR0, 69); // step 4 - 115200 bps^2
    OVERWRITE(UCA1BR1, 0); // step 5 - 115200 bps^2

    SET(UCA1MCTL, UCBRS1); // step 6
    UNSET(UCA1CTL1, UCSWRST); // step 7

    SET(UCA1IE, UCRXIE); // step 8
}

void send_uart_data_int(int data) {
    send_uart_data_byte(data >> 8);
    send_uart_data_byte(data & 0xFF);
}

void update_data_counter() {
    data_counter++;
    if (data_counter == CONFIG->data_length) {
        data_counter = 0;
    }
}

void send_uart_data_byte(char data) {
    if (data_counter == 0) {
        send_uart_prefix();
    }

    send_byte(data);
    update_data_counter();

    if (data_counter == 0) {
        send_uart_suffix();
    }
}
