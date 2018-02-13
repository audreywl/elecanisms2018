#include <p24FJ128GB206.h>
#include "elecanisms.h"
#include <stdio.h>
#include "usb.h"

#define ENC_MISO            D1
#define ENC_MOSI            D0
#define ENC_SCK             D2
#define ENC_CSn             D3

#define ENC_MISO_DIR        D1_DIR
#define ENC_MOSI_DIR        D0_DIR
#define ENC_SCK_DIR         D2_DIR
#define ENC_CSn_DIR         D3_DIR

#define ENC_MISO_RP         D1_RP
#define ENC_MOSI_RP         D0_RP
#define ENC_SCK_RP          D2_RP

#define TOGGLE_LED1         0
#define TOGGLE_LED2         1
#define TOGGLE_LED3         2
#define READ_SW1            3
#define READ_SW2            4
#define READ_SW3            5
#define READ_A0             6
#define SET_DUTY_VAL_FORWARD        7
#define GET_DUTY_VAL_FORWARD        8
#define GET_DUTY_MAX_FORWARD       9
#define SET_DUTY_VAL_REVERSE        10
#define GET_DUTY_VAL_REVERSE        11
#define GET_DUTY_MAX_REVERSE        12
#define ENC_READ_REG       13
#define GET_MICROS         14

WORD micros;

void __attribute__((interrupt, auto_psv)) _T2Interrupt(void) {
    IFS0bits.T2IF = 0;      // lower Timer2 interrupt flag
    micros.w += 1;
    LED1 = !LED1;
}

WORD get_micros(void) {
    return micros;
}

uint16_t even_parity(uint16_t v) {
    v ^= v >> 8;
    v ^= v >> 4;
    v ^= v >> 2;
    v ^= v >> 1;
    return v & 1;
}

WORD enc_readReg(WORD address) {
    WORD cmd, result;
    uint16_t temp;

    cmd.w = 0x4000 | address.w;         // set 2nd MSB to 1 for a read
    cmd.w |= even_parity(cmd.w) << 15;

    ENC_CSn = 0;

    SPI2BUF = (uint16_t)cmd.b[1];
    while (SPI2STATbits.SPIRBF == 0) {}
    temp = SPI2BUF;

    SPI2BUF = (uint16_t)cmd.b[0];
    while (SPI2STATbits.SPIRBF == 0) {}
    temp = SPI2BUF;

    ENC_CSn = 1;

    __asm__("nop");     // p.12 of the AS5048 datasheet specifies a minimum
    __asm__("nop");     //   high time of CSn between transmission of 350ns
    __asm__("nop");     //   which is 5.6 Tcy, so do nothing for 6 Tcy.
    __asm__("nop");
    __asm__("nop");
    __asm__("nop");

    ENC_CSn = 0;

    SPI2BUF = 0;
    while (SPI2STATbits.SPIRBF == 0) {}
    result.b[1] = (uint8_t)SPI2BUF;

    SPI2BUF = 0;
    while (SPI2STATbits.SPIRBF == 0) {}
    result.b[0] = (uint8_t)SPI2BUF;

    ENC_CSn = 1;

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
        case SET_DUTY_VAL_FORWARD:
            OC1R = USB_setup.wValue.w;
            BD[EP0IN].bytecount = 0;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case SET_DUTY_VAL_REVERSE:
            OC2R = USB_setup.wValue.w;
            BD[EP0IN].bytecount = 0;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case GET_DUTY_VAL_FORWARD:
            temp.w = OC1R;
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case GET_DUTY_VAL_REVERSE:
            temp.w = OC2R;
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case GET_DUTY_MAX_FORWARD:
            temp.w = OC1RS;
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case GET_DUTY_MAX_REVERSE:
            temp.w = OC2RS;
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case ENC_READ_REG:
            temp = enc_readReg(USB_setup.wValue);
            BD[EP0IN].address[0] = temp.b[0];
            BD[EP0IN].address[1] = temp.b[1];
            BD[EP0IN].bytecount = 2;
            BD[EP0IN].status = UOWN | DTS | DTSEN;
            break;
        case GET_MICROS:
            temp = get_micros();
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

  // Configure pin D8 to produce a 1-kHz PWM signal with a 25% duty cycle
  // using the OC1 module.
  D8_DIR = OUT;      // configure D8 to be a digital output
  D8 = 0;            // set D8 low
  D7_DIR = OUT;      // configure D7 to be a digital output
  D7 = 0;            // set D7 low

  // Configure encoder pins and connect them to SPI2
  ENC_CSn_DIR = OUT; ENC_CSn = 1;
  ENC_SCK_DIR = OUT; ENC_SCK = 0;
  ENC_MOSI_DIR = OUT; ENC_MOSI = 0;
  ENC_MISO_DIR = IN;

  // Timer 2 Setup for timestamp
  T2CON = 0x0000;         // set Timer2 prescaler to 1
  PR2 = 0x100;            // Period reg 16, resultant period is Tcy * 16, 1us

  TMR2 = 0;               // set Timer2 to 0
  IFS0bits.T2IF = 0;      // lower T2 interrupt flag
  IEC0bits.T2IE = 1;      // enable T2 interrupt
  T2CONbits.TON = 1;      // Start T2

  // ADC setup for higher-speed conversion for current measurement
  AD1CON1bits.SSRC = 3;   // Set conversion trigger to internal timer
  AD1CON2 = 0;            // Don't use an ADC reading buffer, leave volt ref as Vcc -> Vdd
  AD1CON3bits.ADRC = 0;   // Use device clock, not separate RC osc.
  AD1CON3bits.SAMC = 4;   // Set sampling time to 4 TAD a/d converter periods
  AD1CON3bits.ADCS = 1;   // Set TAD to 1 TCY




  RPOR = (uint8_t *)&RPOR0;
  RPINR = (uint8_t *)&RPINR0;

  __builtin_write_OSCCONL(OSCCON & 0xBF);
  RPINR[MISO2_RP] = ENC_MISO_RP;
  RPOR[ENC_MOSI_RP] = MOSI2_RP;
  RPOR[ENC_SCK_RP] = SCK2OUT_RP;
  RPOR[D8_RP] = OC1_RP;  // connect the OC1 module output to pin D8
  RPOR[D7_RP] = OC2_RP;  // connect the OC1 module output to pin D8

  __builtin_write_OSCCONL(OSCCON | 0x40);

  SPI2CON1 = 0x003B;              // SPI2 mode = 1, SCK freq = 8 MHz
  SPI2CON2 = 0;
  SPI2STAT = 0x8000;


  OC1CON1 = 0x1C06;   // configure OC1 module to use the peripheral
                      //   clock (i.e., FCY, OCTSEL<2:0> = 0b111) and
                      //   and to operate in edge-aligned PWM mode
                      //   (OCM<2:0> = 0b110)
  OC1CON2 = 0x001F;   // configure OC1 module to syncrhonize to itself
                      //   (i.e., OCTRIG = 0 and SYNCSEL<4:0> = 0b11111)
  OC2CON1 = 0x1C06;   // configure OC2 module to use the peripheral
                      //   clock (i.e., FCY, OCTSEL<2:0> = 0b111) and
                      //   and to operate in edge-aligned PWM mode
                      //   (OCM<2:0> = 0b110)
  OC2CON2 = 0x001F;   // configure OC2 module to syncrhonize to itself
                      //   (i.e., OCTRIG = 0 and SYNCSEL<4:0> = 0b11111)

  OC1RS = (uint16_t)(FCY / 2e3 - 1.);     // configure period register to
                                          //   get a frequency of 2kHz
  OC2RS = (uint16_t)(FCY / 2e3 - 1.);     // configure period register to
                                          //   get a frequency of 2kHz
  OC1R = 0;  // configure duty cycle to 25% (i.e., period / 4)
  OC2R = 0;

  OC1TMR = 0;         // set OC1 timer count to 0
  OC2TMR = 0;         // set OC1 timer count to 0

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
