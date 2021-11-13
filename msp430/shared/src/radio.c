#include <msp430.h>
#include "radio.h"
#include "nRF.h"

char transmit_buffer[RADIO_PACKET_LENGTH];
unsigned char transmit_counter = 0;
char can_send_data = 1;

void clear_IFG_interrupt() {
    P2IFG &= ~BIT3;
    can_send_data = 1;
}

void clear_IRQ_interrupt() {
    nRF_clear_IRQ();
}

void setup_radio_chip() {
    P2DIR |= BIT2; // Set nRF_CE (Chip Enable) pin to output
    P2DIR |= BIT5; // Set nRF_CSN (Chip Select) pin to output
    P2DIR &= ~BIT3;
    P2IE = BIT3;
    P2IES = BIT3;
    P2IFG &= ~BIT3;

    P2DIR |= BIT7; // Set CLK pin to output
    P3DIR |= BIT3; // Set MOSI pin to output
    P3DIR &= ~BIT4;
    // Set MISO pin to input
    P3SEL |= BIT3 + BIT4; // MISO and MOSI pin functionality select
    P2SEL |= BIT7; // CLK pin functionality select
}

void setup_spi() {
    UCA0CTL0 = UCCKPH + UCMSB + UCMST + UCMODE0 + UCSYNC;
    UCA0CTL1 = UCSSEL1 + UCSSEL0 + UCSWRST;
    UCA0BR0 = 1; // clock prescaler = 1 --> CLK = SMCLK
    UCA0BR1 = 0; //
    UCA0CTL1 &= ~UCSWRST; // bring the state machine output of reset
}

void setup_nRF() {
    nRF_init();
    nRF_clear_IRQ();
}

void init_radio() {
    setup_radio_chip();
    setup_spi();
    setup_nRF();
}

void setup_transmit_mode() {
    init_radio();
    nRF_set_TX_mode();
    nRF_CE_low;
}

void setup_receive_mode() {
    init_radio();
    nRF_set_RX_mode();
    nRF_CE_high;
}

void send_radio_data(const char* buffer) {
    nRF_upload_TX_payload(buffer);
    nRF_CE_high;
    __delay_cycles(85); // must be at least 10 us, 80 is minimum for 8MHz
    nRF_CE_low;
    clear_IRQ_interrupt();

    while(!can_send_data);
    nRF_clear_IRQ();
}

void send_radio_byte_data(char data) {
    transmit_buffer[transmit_counter] = data;
    transmit_counter++;

    if (transmit_counter == RADIO_PACKET_LENGTH) {
        transmit_counter = 0;
        send_radio_data(transmit_buffer);
    }
}

void send_radio_int_data(int data) {
    send_radio_byte_data(data >> 8);
    send_radio_byte_data(data & 0xFF);
}

void receive_radio_data(char* buffer) {
    nRF_download_RX_payload(buffer);
    clear_IRQ_interrupt();
}
