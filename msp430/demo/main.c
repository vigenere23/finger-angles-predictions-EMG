#include <msp430.h> 
#include <stdlib.h>
#include "clock.h"
#include "utils.h"
#include "adc.h"
#include "uart.h"

/* DEMO */


int should_receive_data = 0;

void receive_data() {
    should_receive_data = 0;

    int data1 = get_adc_value(ADC_CHANNEL_0);
    int data2 = get_adc_value(ADC_CHANNEL_1);

    send_uart_data_int(data1);
    send_uart_data_int(data2);
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

    setup_adc();
    setup_clock(CLOCK_FREQUENCY);
    setup_timer(CLOCK_FREQUENCY, 2000);
    setup_uart(&UART_CONFIG);

    __bis_SR_register(GIE);

    while (1) {
        if (should_receive_data) {
            receive_data();
        }
    }
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void TIMER_A0_ISR (void) {
    should_receive_data = 1;
}
