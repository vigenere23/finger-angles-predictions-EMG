#ifndef UART_H_
#define UART_H_


typedef struct UARTConfig {
    char sync_byte;
    char channels;
    char data_length;
    char message_length;
    char check_byte;
} UARTConfig;


void setup_uart(const UARTConfig* config);

void send_uart_data_byte(char data);

void send_uart_data_int(int data);


#endif /* UART_H_ */
