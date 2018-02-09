#include <p24FJ128GB206.h>
#include "elecanisms.h"
#include <stdio.h>
#include "usb.h"

#define TOGGLE_LED1         0
#define TOGGLE_LED2         1
#define TOGGLE_LED3         2
#define READ_SW1            3
#define READ_SW2            4
#define READ_SW3            5
#define READ_A0             6
#define SET_DUTY_VAL        7
#define GET_DUTY_VAL        8
#define GET_DUTY_MAX        9
#define READ_ENCODER       10

WORD32 millis = 0;

void __attribute__((interrupt, auto_psv)) _T2Interrupt(void) {
    IFS0bits.T2IF = 0;      // lower Timer2 interrupt flag
    millis += 1;
}

WORD32 get_millis(void) {
    return millis;
}

WORD enc_readReg(WORD address) {
    WORD cmd, result;
    cmd.w = 0x4000|address.w; //set 2nd MSB to 1 for a read
    cmd.w |= parity(cmd.w)<<15; //calculate even parity for

    //lower the chip select line to start transfer
    D3 = 0;
    SPI1BUF = (uint16_t)cmd.b[1];
    while (SPI1STATbits.SPIRBF ==0) {}
    result.b[1] = (uint8_t)SPI1BUF;
    SPI1BUF = (uint16_t)cmd.b[0];
    while (SPI1STATbits.SPIRBF ==0) {}
    result.b[0] = (uint8_t)SPI1BUF;
    D3 = 1;

    D3 = 0;
    SPI1BUF = 0;
    while (SPI1STATbits.SPIRBF ==0) {}
    result.b[1] = (uint8_t)SPI1BUF;
    SPI1BUF = 0;
    while (SPI1STATbits.SPIRBF ==0) {}
    result.b[0] = (uint8_t)SPI1BUF;
    D3 = 1;

    return result;
}

void vendor_requests(void) {
    WORD temp;
    uint16_t i;

    switch (USB_setup.bRequest) {
        case TOGGLE_LED1:
            LED1 = !LED1;
            BD[EP0IN].bytecount = 0;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case TOGGLE_LED2:
            LED2 = !LED2;
            BD[EP0IN].bytecount = 0;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case TOGGLE_LED3:
            LED3 = !LED3;
            BD[EP0IN].bytecount = 0;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case READ_SW1:
            BD[EP0IN].address[0] = SW1 ? 1 : 0;
            BD[EP0IN].bytecount = 1;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case READ_SW2:
            BD[EP0IN].address[0] = SW2 ? 1 : 0;
            BD[EP0IN].bytecount = 1;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case READ_SW3:
            BD[EP0IN].address[0] = SW3 ? 1 : 0;
            BD[EP0IN].bytecount = 1;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case READ_A0:
            temp.w = read_analog(A0_AN);
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case SET_DUTY_VAL:
            OC1R = USB_setup.wValue.w;
            BD[EP0IN].bytecount = 0;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case GET_DUTY_VAL:
            temp.w = OC1R;
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case GET_DUTY_MAX:
            temp.w = OC1RS;
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case READ_ENCODER:
            temp = enc_readReg(USB_setup.wValue);
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        default:
            USB_error_flags |= REQUEST_ERROR;
    }
}



int16_t main(void) {
  uint8_t *RPOR, *RPINR;

  init_elecanisms();

  D0_DIR = OUT; //MOSI
  D1_DIR = IN;  //MISO
  D2_DIR = OUT; //SCK
  D3_DIR = OUT; //NCS

  //ENC_NCS = 1; //Raise the chip select line (it's active low).
  D3 = 1;

  // Configure pin D8 to produce a 1-kHz PWM signal with a 25% duty cycle
  // using the OC1 module.
  D8_DIR = OUT;      // configure D8 to be a digital output
  D8 = 0;            // set D8 low

  // Timer 2 Setup
  T2CON = 0x0030;         // set Timer2 period to 10 ms for debounce
  PR2 = 0x3E80;           // prescaler 256, match value

  TMR2 = 0;               // set Timer2 to 0
  IFS0bits.T2IF = 0;      // lower T2 interrupt flag
  IEC0bits.T2IE = 1;      // enable T2 interrupt
  T2CONbits.TON = 0;      // make sure T2 isn't on

  RPOR = (uint8_t *)&RPOR0;
  RPINR = (uint8_t *)&RPINR0;

  __builtin_write_OSCCONL(OSCCON & 0xBF);
  RPOR[D0_RP] = MOSI1_RP; // setup SPI pins w/oscillator
  RPINR[MISO1_RP] = D1_RP;
  RPOR[D2_RP] = SCK1OUT_RP;
  RPOR[D8_RP] = OC1_RP;  // connect the OC1 module output to pin D8
  __builtin_write_OSCCONL(OSCCON | 0x40);

  SPI1CON1 = 0x0032;              // SPI mode = 1, SCK freq = 1 MHz
  SPI1CON2 = 0;
  SPI1STAT = 0x8000;

  OC1CON1 = 0x1C06;   // configure OC1 module to use the peripheral
                      //   clock (i.e., FCY, OCTSEL<2:0> = 0b111) and
                      //   and to operate in edge-aligned PWM mode
                      //   (OCM<2:0> = 0b110)
  OC1CON2 = 0x001F;   // configure OC1 module to syncrhonize to itself
                      //   (i.e., OCTRIG = 0 and SYNCSEL<4:0> = 0b11111)

  OC1RS = (uint16_t)(FCY / 1e3 - 1.);     // configure period register to
                                          //   get a frequency of 1kHz
  OC1R = OC1RS >> 2;  // configure duty cycle to 25% (i.e., period / 4)
  OC1TMR = 0;         // set OC1 timer count to 0

  USB_setup_vendor_callback = vendor_requests;
  init_usb();

  while (USB_USWSTAT != CONFIG_STATE) {
#ifndef USB_INTERRUPT
    usb_service();
#endif
  }
  while (1) {
#ifndef USB_INTERRUPT
    usb_service();
#endif
  }
}
