
#include "nRF.h"

//------------------------------------
// nRF24L01+ TX mode settings
void nRF_set_TX_mode(void)
{
    char data[5];
    unsigned int i;
    //++++++++++++++++++++++++++
    // CONFIG : Configuration Register
    data[0] = 0x1A;
    nRF_reg_write(0x00,data,1);
    //++++++++++++++++++++++++++
    for(i = 0 ; i < 65000; i++);
    //++++++++++++++++++++++++++
    // EN_AA : Enhanced ShockBurst
    data[0] = 0x00;
    nRF_reg_write(0x01,data,1);
    //++++++++++++++++++++++++++
    // EN_RXADDR : Enabled RX Addresses
    data[0] = 0x01;
    nRF_reg_write(0x02,data,1);
    //++++++++++++++++++++++++++
    // SETUP_AW : Setup of Address Widths
    data[0] = 0x01;
    nRF_reg_write(0x03,data,1);
    //++++++++++++++++++++++++++
    // SETUP_RETR : Setup of Automatic Retransmission
    data[0] = 0x00;
    nRF_reg_write(0x04,data,1);
    //++++++++++++++++++++++++++
    // RF_CH : RF Channel
    data[0] = 0x68;
    nRF_reg_write(0x05,data,1);
    //++++++++++++++++++++++++++
    // RF_SETUP : RF Setup Register
    data[0] = 0x0F;
    nRF_reg_write(0x06,data,1);
    //++++++++++++++++++++++++++
    // STATUS : Status Register
    //++++++++++++++++++++++++++
    // OBSERVE_TX : Transmit observe register
    //++++++++++++++++++++++++++
    // RPD : Received Power Detector
    //++++++++++++++++++++++++++
    // RX_ADDR_P0 : Receive address data pipe 0
    data[0] = 0x0F;
    data[1] = 0x0E;
    data[2] = 0x0F;
    data[3] = 0x0E;
    data[4] = 0x0F;
    nRF_reg_write(0x0A,data,5);
    //++++++++++++++++++++++++++
    // RX_ADDR_P1 : Receive address data pipe 1 
    //++++++++++++++++++++++++++
    // RX_ADDR_P2 : Receive address data pipe 2
    //++++++++++++++++++++++++++
    // RX_ADDR_P3 : Receive address data pipe 3
    //++++++++++++++++++++++++++
    // RX_ADDR_P4 : Receive address data pipe 4
    //++++++++++++++++++++++++++
    // RX_ADDR_P5 : Receive address data pipe 5
    //++++++++++++++++++++++++++
    // TX_ADDR : Transmit address
    data[0] = 0x0F;
    data[1] = 0x0E;
    data[2] = 0x0F;
    data[3] = 0x0E;
    data[4] = 0x0F;
    nRF_reg_write(0x10,data,5);
    //++++++++++++++++++++++++++
    // RX_PW_P0 : Number of bytes in RX payload in data pipe 0 ????????????
    data[0] = nRF_packet_len;
    nRF_reg_write(0x11,data,1);
    //++++++++++++++++++++++++++
    // RX_PW_P1 : Number of bytes in RX payload in data pipe 1
    //++++++++++++++++++++++++++
    // RX_PW_P2 : Number of bytes in RX payload in data pipe 2
    //++++++++++++++++++++++++++
    // RX_PW_P3 : Number of bytes in RX payload in data pipe 3
    //++++++++++++++++++++++++++
    // RX_PW_P4 : Number of bytes in RX payload in data pipe 4
    //++++++++++++++++++++++++++
    // RX_PW_P5 : Number of bytes in RX payload in data pipe 5
    //++++++++++++++++++++++++++
    // FIFO_STATUS : FIFO Status Register
    //++++++++++++++++++++++++++
    // DYNPD : Enable dynamic payload length
    data[0] = 0x00;
    nRF_reg_write(0x1C,data,1);
    //++++++++++++++++++++++++++
    // FEATURE : Feature Register
    data[0] = 0x00;
    nRF_reg_write(0x1D,data,1);
    //++++++++++++++++++++++++++
}
//------------------------------------
// nRF24L01+ RX mode settings
void nRF_set_RX_mode(void)
{
    char data[5];
    unsigned int i;
    //++++++++++++++++++++++++++
    // CONFIG : Configuration Register
    data[0] = 0x1B;
    nRF_reg_write(0x00,data,1);
    //++++++++++++++++++++++++++
    for(i = 0 ; i < 65000; i++);
    //++++++++++++++++++++++++++
    // EN_AA : Enhanced ShockBurst
    data[0] = 0x00;
    nRF_reg_write(0x01,data,1);
    //++++++++++++++++++++++++++
    // EN_RXADDR : Enabled RX Addresses
    data[0] = 0x01;
    nRF_reg_write(0x02,data,1);
    //++++++++++++++++++++++++++
    // SETUP_AW : Setup of Address Widths
    data[0] = 0x01;
    nRF_reg_write(0x03,data,1);
    //++++++++++++++++++++++++++
    // SETUP_RETR : Setup of Automatic Retransmission
    data[0] = 0x00;
    nRF_reg_write(0x04,data,1);
    //++++++++++++++++++++++++++
    // RF_CH : RF Channel
    data[0] = 0x68;
    nRF_reg_write(0x05,data,1);
    //++++++++++++++++++++++++++
    // RF_SETUP : RF Setup Register
    data[0] = 0x0E;
    nRF_reg_write(0x06,data,1);
    //++++++++++++++++++++++++++
    // STATUS : Status Register
    //++++++++++++++++++++++++++
    // OBSERVE_TX : Transmit observe register
    //++++++++++++++++++++++++++
    // RPD : Received Power Detector
    //++++++++++++++++++++++++++
    // RX_ADDR_P0 : Receive address data pipe 0
    data[0] = 0x0F;
    data[1] = 0x0E;
    data[2] = 0x0F;
    data[3] = 0x0E;
    data[4] = 0x0F;
    nRF_reg_write(0x0A,data,5);
    //++++++++++++++++++++++++++
    // RX_ADDR_P1 : Receive address data pipe 1 
    //++++++++++++++++++++++++++
    // RX_ADDR_P2 : Receive address data pipe 2
    //++++++++++++++++++++++++++
    // RX_ADDR_P3 : Receive address data pipe 3
    //++++++++++++++++++++++++++
    // RX_ADDR_P4 : Receive address data pipe 4
    //++++++++++++++++++++++++++
    // RX_ADDR_P5 : Receive address data pipe 5
    //++++++++++++++++++++++++++
    // TX_ADDR : Transmit address
    data[0] = 0x0F;
    data[1] = 0x0E;
    data[2] = 0x0F;
    data[3] = 0x0E;
    data[4] = 0x0F;
    nRF_reg_write(0x10,data,5);
    //++++++++++++++++++++++++++
    // RX_PW_P0 : Number of bytes in RX payload in data pipe 0 ????????????
    data[0] = nRF_packet_len;
    nRF_reg_write(0x11,data,1);
    //++++++++++++++++++++++++++
    // RX_PW_P1 : Number of bytes in RX payload in data pipe 1
    //++++++++++++++++++++++++++
    // RX_PW_P2 : Number of bytes in RX payload in data pipe 2
    //++++++++++++++++++++++++++
    // RX_PW_P3 : Number of bytes in RX payload in data pipe 3
    //++++++++++++++++++++++++++
    // RX_PW_P4 : Number of bytes in RX payload in data pipe 4
    //++++++++++++++++++++++++++
    // RX_PW_P5 : Number of bytes in RX payload in data pipe 5
    //++++++++++++++++++++++++++
    // FIFO_STATUS : FIFO Status Register
    //++++++++++++++++++++++++++
    // DYNPD : Enable dynamic payload length
    data[0] = 0x00;
    nRF_reg_write(0x1C,data,1);
    //++++++++++++++++++++++++++
    // FEATURE : Feature Register
    data[0] = 0x00;
    nRF_reg_write(0x1D,data,1);
    //++++++++++++++++++++++++++
}
//------------------------------------













