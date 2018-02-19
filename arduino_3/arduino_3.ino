#include <Wire.h>
#include <Adafruit_ADS1015.h>

Adafruit_ADS1115 ads;  /* Use this for the 16-bit version */
//Adafruit_ADS1015 ads;     /* Use thi for the 12-bit version */

void setup(void)
{
  Serial.begin(9600);
  //Serial.println("Hello!");

  //Serial.println("Getting single-ended readings from AIN0..1");
  //Serial.println("ADC Range: +/- 4.096V ( 0.125mV/ADS1115)");

  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!


  ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 0.125mV
  ads.begin();
}

double voltage(){
  int16_t adc0;
  adc0 = ads.readADC_SingleEnded(0);
  return (adc0 * 0.000125 * 10.10101);
}

double current(){
  int16_t adc1;
  adc1 = ads.readADC_SingleEnded(1);
  return (adc1 * 0.000125 * 18.0018); 
}
void loop(void)
{
  Serial.print(voltage()); Serial.print(','); //10.10101
  Serial.println(current());//  Serial.println('A'); //18.0018
}
