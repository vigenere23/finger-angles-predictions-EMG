#ifndef UART_H_
#define UART_H_


void setup_uart();

void send_uart_data(char *data, unsigned char length, char start_bit, char end_bit);

void send_uart_byte(char byte);


#endif /* UART_H_ */
