#ifndef INCLUDE_RADIO_H_
#define INCLUDE_RADIO_H_

#include "nRF.h"

#define RADIO_PACKET_LENGTH nRF_packet_len

void clear_IFG_interrupt();

void setup_radio_transmit_mode();

void setup_radio_receive_mode();

void send_radio_int_data(int data);

void send_radio_byte_data(char data);

void receive_radio_data(char* buffer);

#endif /* INCLUDE_RADIO_H_ */
