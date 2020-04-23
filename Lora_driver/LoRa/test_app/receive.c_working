#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>
#include <sys/select.h>

#include "lora-ioctl.h"

/* Bit 1: 1 for ready to read, 0 for not ready
 * Bit 0: 1 for ready to write, 0 for not write
 */
uint8_t ready2rw(int fd)
{
	fd_set read_fds, write_fds;
	struct timeval tv = {.tv_sec = 5, .tv_usec = 0};
	uint8_t flag;

	/* I/O multiplexing. */
	FD_ZERO(&read_fds);
	FD_ZERO(&write_fds);
	FD_SET(fd, &read_fds);
	FD_SET(fd, &write_fds);
	if (select(fd+1, &read_fds, &write_fds, NULL, &tv) == -1)
		perror("Select failed");

	flag = 0;
	/* Read from the file descriptor if it is ready to be read. */
	if (FD_ISSET(fd, &read_fds)) {
		flag |= (1 << 1);
	}
	/* Write to the file descriptor if it is ready to be written. */
	if (FD_ISSET(fd, &write_fds)) {
		flag |= (1 << 0);
	}

	return flag;
}


static float NtcTempCode[166] =
{
	401859.72, 373810.23, 347932.61, 324043.24, 301975.23, 281576.83, 262709.96, 245248.87,
	229078.96, 214095.75, 200203.90, 187316.35, 175353.57, 164242.82, 153917.57, 144316.94,
	135385.12, 127070.98, 119327.64, 112112.05, 105384.69, 99109.27, 93252.39, 87783.38,
	82673.95, 77898.11, 73431.86, 69253.12, 65341.48, 61678.14, 58245.71, 55028.16, 
	52010.63, 49179.41, 46521.80, 44026.05, 41681.25, 39477.34, 37404.94, 35455.38,
	33620.60, 31893.14, 30266.03, 28732.84, 27287.54, 25924.56, 24638.71,
	23425.14, 22279.34, 21197.13, 20174.58, 19208.04, 18294.10, 17429.59,
	16611.53, 15837.15, 15103.85, 14409.22, 13750.98, 13127.01, 12535.33,
 	11974.06, 11441.48, 10935.95, 10455.94, 10000.00, 9566.80, 9155.06,
	8763.61, 8391.31, 8037.14, 7700.10, 7379.26, 7073.76, 6782.77,
	6505.53, 6241.30, 5989.41, 5749.21, 5520.08, 5301.47, 5092.82,
	4893.63, 4703.42, 4521.73, 4348.14, 4182.23, 4023.64, 3871.99,
	3726.95, 3588.18, 3455.39, 3328.29, 3206.60, 3090.07, 2978.44,
	2871.48, 2768.98, 2670.72, 2576.51, 2486.16, 2399.50, 2316.34,
	2236.53, 2159.93, 2086.37, 2015.74, 1947.88, 1882.70, 1820.05,
	1759.84, 1701.95, 1646.28, 1592.74, 1541.24, 1491.68, 1443.99,
	1398.08, 1353.88, 1311.32, 1270.32, 1230.83, 1192.77, 1156.10,
	1120.75, 1086.67, 1053.81, 1022.11, 991.54, 962.04, 933.58,
	906.10, 879.58, 853.98, 829.25, 805.37, 782.30, 760.00,
	738.46, 717.65, 697.52, 678.06, 659.25, 641.05, 623.45,
	606.42, 589.94, 573.99, 558.55, 543.61, 529.14, 515.13,
	501.56, 488.41, 475.68, 463.34, 451.38, 439.79, 428.55,
	417.65, 407.09, 396.84, 386.91, 377.26, 367.91, 358.83
};

float CalcSensorTemp(uint16_t code)  /// codeUpload temperature code value for sensor
{
	float temp;
	uint8_t i = 0;
	temp = code * 3300/(4095 - code);
	if(temp <= 358.83)				// highest +125 Celsius
		temp = 358.83;
	if(temp >= 401859.72)
		temp = 401859.72;			// lowest  -40 Celsius
	for(i=0; i<165; i++)
	{
		if(temp == NtcTempCode[i])
		{
			temp = (float)i - 40.0;
			break;
		}
		if(temp == NtcTempCode[i+1])
		{
			temp = (float)(i+1) - 40.0;
			break;
		}
		if((temp < NtcTempCode[i]) && (temp > NtcTempCode[i+1]))
		{
			temp = (float)i + (NtcTempCode[i] -temp) /(NtcTempCode[i] - NtcTempCode[i+1]) - 40.0;
			break;
		}
	}
	return temp;
}



char buffer[127];
void HexToAscii(unsigned char *pHex, unsigned char *pAscii, int nLen)
{
    unsigned char Nibble[2];
    unsigned int i,j;
    for (i = 0; i < nLen; i++){
        Nibble[0] = (pHex[i] & 0xF0) >> 4;
        Nibble[1] = pHex[i] & 0x0F;
        for (j = 0; j < 2; j++){
            if (Nibble[j] < 10){            
                Nibble[j] += 0x30;
            }
            else{
                if (Nibble[j] < 16)
                    Nibble[j] = Nibble[j] - 10 + 'A';
            }
            *pAscii++ = Nibble[j];
        }              
    }           
}


uint16_t crc_start(unsigned char *p,unsigned char n)
   {
     int i,j;
  unsigned int flag,crc;
  crc = 0xffff;
  for(i=0;i<n;i++)
     {
   crc^=*p++;
   for(j=0;j<8;j++)
      {
    flag = crc&0x0001;
    crc>>=1;
    crc&=0x7fff;
    if(flag)
      {
       crc^=0xa001;
      }
   }
     }
  flag=crc%256;
  i   =(crc-flag)/256;
  crc =flag*256+i;
  return (crc);
  
   }






#define ready2read(fd)	(ready2rw(fd) & (1 << 1))
#define ready2write(fd)	(ready2rw(fd) & (1 << 0))



int main(int argc, char **argv)
{
	char *path;
	int fd;
	char pstr[40];
	/*
	system("echo 1 >  /sys/class/leds/rst_lora118/brightness");
	system("echo 0 >  /sys/class/leds/rst_lora118/brightness");
	*/
	#define MAX_BUFFER_LEN	127
	char buf[MAX_BUFFER_LEN];
	int len;
	int i;
	unsigned int s;
	/* Parse command. */
	if (argc >= 2) 
	{
		path = argv[1];
	}
	else 
	{
		printf("Need more arguments.\r\n");
		return -1;
	}
	printf("Going to open %s\n", path);
	/* Open device node. */
	fd = open(path, O_RDWR);
	printf("Opened %s\n", path);
	if (fd == -1) 
	{
		sprintf(pstr, "Open %s failed", path);
		perror(pstr);
		return -1;
	}

	/*Set the RF spreading factor. */
	uint32_t freq = 470000000;
	uint32_t bw = 500000;
	uint32_t sprf = 1024;
	int32_t power = 17;
	int32_t cr = 0x46;
	uint8_t crc = 0x01;
	uint8_t hp = 0x0;
	uint32_t pr = 0x4;
	uint8_t optm = 0x1;
	uint32_t lna = 0x1;
	printf("Set parameters FREQ::%u | SP:: %u | BW::%u | PW::%u | CR::%u | CRC:: %u | HOP:: %u | PREM:: %u | OPTM:: %u", freq, sprf, bw, power, cr, crc, hp, pr, optm);
	set_freq(fd, freq);
	set_sprfactor(fd, sprf);
	set_bw(fd, bw);
	set_power(fd, power);
	set_CR(fd, cr);
	set_CRC(fd, crc);
	set_HOP(fd, hp);
	set_PREAMBLE(fd, pr);
	set_OPTM(fd, optm);
	set_lna(fd,lna);

	/* Read paremetersfrom the file descriptor */
	printf("The LoRa carrier frequency is %u Hz\n", get_freq(fd));
	printf("The RF spreading factor is %u chips\n", get_sprfactor(fd));
	printf("The RF bandwith is %u Hz\n", get_bw(fd));
	printf("The output power is %d dbm\n", get_power(fd));
	printf("The LNA gain is %d db\n", get_lna(fd));
	printf("The current RSSI is %d dbm\n", get_rssi(fd));
	printf("The CR Value is 0x%X Rate\n", get_CR(fd));
	printf("The current HOP is %d Point \n", get_HOP(fd));
	printf("The LoRa PREAMABLE  0x%X LENGTH \n", get_PREAMBLE(fd));
	printf("The LoRa SNR  %d Db \n", get_snr(fd));
	printf("The LoRa LAST PACKET RSSI  %d Db \n", get_LPKTRSSI(fd));
	/* Set the device in read state. */
	set_state(fd, LORA_STATE_RX);
	printf("The LoRa device is in 0x%X state\n", get_state(fd));





	
	
	for(;;)
	{
		memset(buf, 0, MAX_BUFFER_LEN);
		printf("Going to read %s\n", path);
		s = 0;
		while (!ready2read(fd)) {
			sleep(1);
			s++;
			printf("\t%s is not ready to read, do other things.", path);
			printf("  %u s\r", s);
		}
		printf("\n");
		len = do_read(fd, buf, MAX_BUFFER_LEN - 1);
		if (len > 0) 
		{
			HexToAscii(buf, buffer, len);
			printf("1--------Received ::%c%c-%c%c-%c%c-%c%c-%c%c-%c%c-%c%c\n", buffer[0],buffer[1],buffer[2],buffer[3],buffer[4],buffer[5],buffer[6],buffer[7],buffer[8],buffer[9],buffer[10],buffer[11],buffer[12],buffer[13]);
			if(buf[0]==0xac){
			unsigned int crcCheck = crc_start(buf+1,len-3);
			printf("crcCheck  %X\n",crcCheck);
			if((((crcCheck&0xff00)>>8)==buf[5])&&((crcCheck&0xff)==buf[6]))
			  {
          if((buf[3]==0xee)&&(buf[4]==0xee))
          {
          	printf("No Power.\n");
          }
         else
         {
          uint16_t TEMP;
          float temprature;
          TEMP = buf[4];
          TEMP = (TEMP<<8)&0XFF00;
          TEMP|= buf[3];
          temprature = CalcSensorTemp(TEMP);
          printf("1--------Received ::%c%c-%c%c\n", buffer[4],buffer[5],buffer[2],buffer[3]);
          printf("Received Temperature:: %f\n",temprature);
         }
        }
			}
			
				printf("\n\n\n\n------------HERE IS THE LORA READ STRING------------\n");
				//printf("Read %d bytes: 0x%X\n", len, buf);
				printf("------------PARAMETERS----------\n");
				printf("The LoRa carrier frequency is %u Hz\n", get_freq(fd));
				printf("The RF spreading factor is %u chips\n", get_sprfactor(fd));
				printf("The RF bandwith is %u Hz\n", get_bw(fd));
				printf("The output power is %d dbm\n", get_power(fd));
				printf("The LNA gain is %d db\n", get_lna(fd));
				printf("The current RSSI is %d dbm\n", get_rssi(fd));
				printf("The CR Value is 0x%X Rate\n", get_CR(fd));
				printf("The current HOP is %d Point \n", get_HOP(fd));
				printf("The LoRa PREAMABLE  0x%X LENGTH \n", get_PREAMBLE(fd));
				printf("The LoRa SNR  %d Db \n", get_snr(fd));
				printf("The LoRa LAST PACKET RSSI  %d Db \n", get_LPKTRSSI(fd));
			
			sleep(1);
			
			/* Echo */
			printf("Going to echo %s\n", path);
			for (i = 0; i < len; i++)
				buf[i] = toupper(buf[i]);
				s = 0;
			/*
			while (!ready2write(fd)) {
				sleep(1);
				s++;
				printf("\t%s is not ready to write, do other things.", path);
				printf("  %u s\r", s);
			}

			printf("\n");
			len = do_write(fd, buf, len);
			printf("Echoed %d bytes: %s\n", len, buf);
			}
			*/	
			sleep(2);
		}
	}
	/* Set the device in sleep state. */
	set_state(fd, LORA_STATE_SLEEP);
	//printf("The LoRa device is in 0x%X state\n", get_state(fd));
	/* Close device node. */
	close(fd);
	return 0;
}
