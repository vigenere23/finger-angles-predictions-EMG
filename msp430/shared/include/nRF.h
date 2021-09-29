
#include <msp430.h>
#include "msp430f5529.h"
//#include "utils.h"

extern void nRF_init(void);

extern void nRF_reg_write(char addr, char *data, unsigned data_length);
extern void nRF_reg_read(char addr, char *data, unsigned data_length);

extern void nRF_upload_TX_payload(char *data);
extern void nRF_download_RX_payload(char *data);

extern void nRF_FLUSH_TX(void);
extern void nRF_FLUSH_RX(void);

extern char nRF_NOP(void);
extern char nRF_FIFO_STATUS(void);

extern void nRF_clear_IRQ(void);

extern char nRF_read_RX_payload_len(void);

extern void nRF_set_TX_mode(void);
extern void nRF_set_RX_mode(void);

extern void nRF_set_STANDBY1_modeRX(void);

extern void wait_for_place_in_tx_fifo(void);
extern void wait_for_empty_tx_fifo(void);


//---------------------------------------------------------------------
#define nRF_DESELECT while(UCB1STAT & UCBUSY); P2OUT |= BIT5
#define nRF_SELECT P2OUT &= ~BIT5

#define nRF_CE_high P2OUT |= BIT2
#define nRF_CE_low P2OUT &= ~BIT2

#define PULSE_CE nRF_CE_high; __delay_cycles(200); nRF_CE_low // The delay value must be set according to the CPU clock frequency and must be at least 10 microseconds


#define nRF_ENTER_RECEIVE_MODE nRF_CE_low; \
							nRF_init(); \
							nRF_set_RX_mode(); \
							nRF_clear_IRQ(); \
							nRF_CE_high

#define nRF_ENTER_TRANSMIT_MODE nRF_CE_low; \
								nRF_init(); \
								nRF_clear_IRQ(); \
								nRF_set_TX_mode()

#define nRF_packet_len 32
//---------------------------------------------------------------------








