#include "nRF.h"
//---------------------------------------------------------------------
char tmp;
void nRF_init(void)
{
	unsigned int i;
    nRF_CE_low;
    for(i = 0 ; i < 65000; i++);
    nRF_SELECT;
    for(i = 0 ; i < 65000; i++);
    nRF_DESELECT;
}
//---------------------------------------------------------------------
void nRF_reg_write(char addr, char *data, unsigned data_length)
{
    char i;
    
    addr = addr & 0x1F;
    addr = addr | 0x20;
    
    nRF_SELECT;
    
    UCA0TXBUF = addr;
    
    for(i = 0; i < data_length; i++)
    {
        while(UCA0STAT & UCBUSY);
        UCA0TXBUF = data[i];
    }
    
    while(UCA0STAT & UCBUSY);
    nRF_DESELECT;
    
    //SPI_buffer_flush();
}
//---------------------------------------------------------------------
void nRF_reg_read(char addr, char *data, unsigned data_length)
{
    char i;
    
    addr = addr & 0x1F;
    
    //SPI_buffer_flush();
    
    nRF_SELECT;
    
    UCA0TXBUF = addr;
    while(UCA0STAT & UCBUSY);
    tmp = UCA0RXBUF;
    
    for(i = 0; i < data_length; i++)
    {
        UCA0TXBUF = 0xFF;
        while(UCA0STAT & UCBUSY);
        *(data+i) = UCA0RXBUF;
    }
    
    while(UCA0STAT & UCBUSY);
    nRF_DESELECT;    
}
//---------------------------------------------------------------------
void nRF_upload_TX_payload(char *data)
{
    char i;

    __bic_SR_register(GIE);  // stop all interrupts

    nRF_SELECT;

    UCA0TXBUF =  0xA0;
    for(i = 0; i < nRF_packet_len; i++)
    {
        while(UCA0STAT & UCBUSY);
        UCA0TXBUF = data[i];
    }

    while(UCA0STAT & UCBUSY);
    nRF_DESELECT;

    __bis_SR_register(GIE); // reactivate all interrupts

    //SPI_buffer_flush();
}
//---------------------------------------------------------------------
void nRF_download_RX_payload(char *data)
{
    char i;
    
    //SPI_buffer_flush();
    
    nRF_SELECT;
    
    UCA0TXBUF =  0x61;
    while(UCA0STAT & UCBUSY);
    tmp = UCA0RXBUF;
    
    for(i = 0; i < nRF_packet_len; i++)
    {
        UCA0TXBUF = 0xFF;
        while(UCA0STAT & UCBUSY);
        *(data+i) = UCA0RXBUF;
    }
    
    while(UCA0STAT & UCBUSY);
    nRF_DESELECT;   
}
//---------------------------------------------------------------------
void nRF_FLUSH_TX(void)
{
    nRF_SELECT;
    
    UCA0TXBUF =  0xE1;
    while(UCA0STAT & UCBUSY);
    tmp = UCA0RXBUF;
    
    nRF_DESELECT;
}
//---------------------------------------------------------------------
void nRF_FLUSH_RX(void)
{
    nRF_SELECT;
    
    UCA0TXBUF =  0xE2;
    while(UCA0STAT & UCBUSY);
    tmp = UCA0RXBUF;
    
    nRF_DESELECT;
}
//---------------------------------------------------------------------
char nRF_NOP(void)
{
    char status;
    
    nRF_SELECT;
    
    UCA0TXBUF = 0xFF;
    while(UCA0STAT & UCBUSY);
    status = UCA0RXBUF;
    
    nRF_DESELECT;
    
    return status;
}
//---------------------------------------------------------------------
char nRF_FIFO_STATUS(void)
{
    char status;

    nRF_SELECT;

    UCA0TXBUF =  0x17;
	while(UCA0STAT & UCBUSY);
	tmp = UCA0RXBUF;

	UCA0TXBUF = 0xFF;
	while(UCA0STAT & UCBUSY);
	status = UCA0RXBUF;

    nRF_DESELECT;

    return status;
}
//---------------------------------------------------------------------
char nRF_read_RX_payload_len(void)
{
    char length;
    
    nRF_SELECT;
    
    UCA0TXBUF =  0x60;
    while(UCA0STAT & UCBUSY);
    tmp = UCA0RXBUF;
    
    UCA0TXBUF = 0xFF;
    while(UCA0STAT & UCBUSY);
    length = UCA0RXBUF;
    
    nRF_DESELECT;
    
    return length;
}
//---------------------------------------------------------------------
void nRF_clear_IRQ(void)
{
    nRF_SELECT;
    
    UCA0TXBUF =  0x27;
    while(UCA0STAT & UCBUSY);
    tmp = UCA0RXBUF;
    
    UCA0TXBUF =  0x70;
    while(UCA0STAT & UCBUSY);
    tmp = UCA0RXBUF;
    
    nRF_DESELECT;
}
//---------------------------------------------------------------------
void nRF_set_STANDBY1_modeRX(void)
{
	char data =0x19;
	nRF_CE_high;
	nRF_reg_write(0x00, &data, 1);
}
//---------------------------------------------------------------------
void wait_for_place_in_tx_fifo(void)
{
	volatile char fifo_status;
	fifo_status = nRF_FIFO_STATUS();
	while(fifo_status & 0x20)
	{
		__delay_cycles(100);
		fifo_status = nRF_FIFO_STATUS();
	}
}
//---------------------------------------------------------------------
void wait_for_empty_tx_fifo(void)
{
	volatile char fifo_status;
	fifo_status = nRF_FIFO_STATUS(); // Check the fifo status of the transceiver
	while(!(fifo_status & 0x10))
	{
		__delay_cycles(100);
		fifo_status = nRF_FIFO_STATUS();
	}
}













