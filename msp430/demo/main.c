#include <msp430.h> 
#include <stdlib.h>
#include "clock.h"
#include "utils.h"
#include "adc.h"
#include "uart.h"


int should_send_data = 0;

void send_data() {
    should_send_data = 0;

    // int data = get_adc_value();
    int data = rand();

    if (data >= 1500) { // ~1V
        SET(P4OUT, BIT7);
    } else {
        UNSET(P4OUT, BIT7);
    }

    char lsb = data >> 8;
    char msb = data & 0xFF;

    char bytes[] = { lsb, msb };

    send_uart_data(bytes, 2, 1, 254);
}

int main(void)
{
    const long CLOCK_FREQUENCY = 8000000;

    WDTCTL = WDTPW | WDTHOLD;

    OUTPUT(P4DIR, BIT7);

    setup_adc();
    setup_clock(CLOCK_FREQUENCY);
    setup_timer(CLOCK_FREQUENCY, 500);
    setup_uart();

    __bis_SR_register(GIE);

    while (1) {
        if (should_send_data) {
            send_data();
        }
    }
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void TIMER_A0_ISR (void) {
    should_send_data = 1;
}
