#include <msp430.h> 
#include <stdlib.h>
#include "clock.h"
#include "utils.h"
#include "adc.h"
#include "uart.h"


int should_send_data = 0;

void send_data() {
    should_send_data = 0;

    // TODO implement ADC for multiple channels
    // int data1 = get_adc_value();
    // int data2 = get_adc_value();
    int data1 = rand();
    int data2 = rand();

    send_uart_data_int(data1);
    send_uart_data_int(data2);
}

int main(void)
{
    const long CLOCK_FREQUENCY = 8000000;
    const UARTConfig UART_CONFIG = {
        .sync_byte = '\n',
        .channels = 2,
        .data_length = 64,
        .message_length = 2,
        .check_byte = 0xFF
    };

    WDTCTL = WDTPW | WDTHOLD;

    OUTPUT(P4DIR, BIT7);

    setup_adc();
    setup_clock(CLOCK_FREQUENCY);
    setup_timer(CLOCK_FREQUENCY, 500);
    setup_uart(&UART_CONFIG);

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
