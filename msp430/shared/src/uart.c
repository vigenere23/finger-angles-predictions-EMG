#include <uart.h>
#include <utils.h>
#include <msp430.h>


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
