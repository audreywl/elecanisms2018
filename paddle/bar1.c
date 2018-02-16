#include <p24FJ64GB002.h>

_CONFIG1(FWDTEN_OFF & WINDIS_OFF & ICS_PGx1 & GWRP_ON & GCP_OFF & JTAGEN_OFF);
_CONFIG2(POSCMOD_NONE & I2C1SEL_PRI & IOL1WAY_OFF & OSCIOFNC_OFF & FCKSM_CSECME & FNOSC_FRCPLL & PLL96MHZ_ON & PLLDIV_NODIV & IESO_ON);
_CONFIG3(SOSCSEL_IO & WUTSEL_LEG & WPDIS_WPDIS & WPCFG_WPCFGDIS);
_CONFIG4(RTCOSC_LPRC & DSBOREN_OFF & DSWDTEN_OFF);

typedef union {
	long l;
	unsigned long ul;
	unsigned int w[2];
        unsigned char b[4];
} word32;

int main(void) {
    unsigned int servo;

//    CLKDIV = 0x0140;    // RCDIV = 001 (4MHz, div2), CPDIV = 01 (FOSC = 16MHz, FCY = 8MHz)
    CLKDIV = 0x0100;    // RCDIV = 001 (4MHz, div2), CPDIV = 00 (FOSC = 32MHz, FCY = 16MHz)

    AD1PCFG = 0xFFDF;   // Make AN5 (pin 7) an analog input and make all other pins digital I/Os
    TRISA = 0x0000;     // Make all PORTA pins digital outputs
    PORTA = 0x0000;     // Clear all PORTA pins
    TRISB = 0xFFFF;     // Make all PORTB pins (except RB3/RA5/pin 7) digital inputs

    __builtin_write_OSCCONL(OSCCON&0xBF);   // Unlock RP registers
    RPOR2bits.RP5R = 18;                    // Assign OC1 to RP5 (pin 2)
    __builtin_write_OSCCONL(OSCCON|0x40);   // Lock RP registers

    OC1CON1 = 0;                    // Clear OC1 configuration bits in preparation to conifgure it
    OC1CON2 = 0;
    OC1CON1bits.OCTSEL = 0b111;     // Set OC1 Timer select bits to System Clock
    OC1CON1bits.TRIGMODE = 1;       // Set OC1 TRIGSTAT to be cleared when its timer overflows
    OC1CON2bits.OCTRIG = 1;         // Set OC1 to trigger off...
    OC1CON2bits.SYNCSEL = 0b01011;  // ...of Timer1
    OC1R = 1;                       // Set OC1 to go high when OC1TMR equals 1
    servo = 0x8000;                 // Set servo position to neutral (represented as a 16-bit fixed-point fraction)
    OC1RS = 0x4000+(servo>>2);      // Set OC1 pulse width to reflect the value in servo
    OC1CON1bits.OCM = 0b111;        // Set OC1 to operate in center-aligned PWM mode

    PR1 = 5000;         // Set Timer1 period register so Timer1 goes off in intervals of 20ms
    T1CON = 0x8020;     // Configure and enable Timer1 (TCKPS<1:0> = 10, prescalar of 1:64)

    while (1) {
        while (IFS0bits.T1IF==0) {}
        IFS0bits.T1IF = 0;
        PORTAbits.RA1 = !PORTAbits.RA1;
    }
}
