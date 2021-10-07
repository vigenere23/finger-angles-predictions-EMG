#include <msp430.h>
#include "uart.h"
#include "utils.h"


void setup_uart() {
    SET(P4SEL, BIT4 + BIT5); // step 1
    SET(UCA1CTL1, UCSWRST); // step 2
    SET(UCA1CTL1, UCSSEL__SMCLK); // step 3

    // baud rate = 8000000 / (UCA1BR1 * 256 + UCA1BR0)
    // <=> UCA1BR1 * 256 + UCA1BR0 = 8 000 000 / 115200 = 69.4444
    OVERWRITE(UCA1BR0, 69); // step 4 - 115200 bps^2
    OVERWRITE(UCA1BR1, 0); // step 5 - 115200 bps^2

    SET(UCA1MCTL, UCBRS1); // step 6
    UNSET(UCA1CTL1, UCSWRST); // step 7

    SET(UCA1IE, UCRXIE); // step 8
}

void send_uart_data(char *data, unsigned char length, char start_bit, char end_bit) {
    send_uart_byte(start_bit);

    while (length > 0) {
        send_uart_byte(*data);
        length--;
        data++;
    }

    send_uart_byte(end_bit);

    // TODO needed?
    // while(UCA1STAT & UCBUSY); // wait for last byte to be sent
}

void send_uart_byte(char byte) {
    while(!(UCA1IFG & UCTXIFG)); // Wait for TX buffer to be ready for new data
    UCA1TXBUF = byte; // put data in buffer
}
