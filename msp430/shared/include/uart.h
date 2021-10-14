#ifndef UART_H_
#define UART_H_


void setup_uart();

void send_uart_data(char *data, unsigned char length, char start_byte, char end_byte);

void send_uart_byte(char byte);


#endif /* UART_H_ */
