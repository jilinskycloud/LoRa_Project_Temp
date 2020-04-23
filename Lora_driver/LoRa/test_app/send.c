#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
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

#define ready2read(fd)	(ready2rw(fd) & (1 << 1))
#define ready2write(fd)	(ready2rw(fd) & (1 << 0))

int main(int argc, char **argv)
{
	char *path;
	char *data;
	int fd;
	char pstr[40];
#define MAX_BUFFER_LEN	127
	char buf[MAX_BUFFER_LEN];
	int len;
	unsigned int s;

	/* Parse command. */
	if (argc >= 3) {
		path = argv[1];
		data = argv[2];
	}
	else {
		printf("Need more arguments.\r\n");
		return -1;
	}
	printf("Going to open %s\n", path);
	/* Open device node. */
	fd = open(path, O_RDWR);
	printf("Opened %s\n", path);
	if (fd == -1) {
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
	/* Set the device in read state. */
	set_state(fd, LORA_STATE_TX);
	printf("The LoRa device is in 0x%X state\n", get_state(fd));

	for(;;){
		sleep(1);
		while (!ready2write(fd)) {
			sleep(1);
			s++;
			printf("\t%s is not ready to write, do other things.", path);
			printf("  %u s\r", s);
		}
		len = do_write(fd, data, strlen(data));
		printf("Written %d bytes: %s\n", len, data);
		/* Read from echo if it is ready to be read. */
		memset(buf, 0, MAX_BUFFER_LEN);
		s = 0;
		/*
		while (!ready2read(fd)) {
			sleep(1);
			s++;
			printf("\t%s is not ready to read, do other things.", path);
			printf("  %u s\r", s);
		}
		printf("\n");
		len = do_read(fd, buf, MAX_BUFFER_LEN - 1);
		if (len > 0)
			printf("Read %d bytes: %s\n", len, buf);
		*/
		printf("\n\n\n\n------------HERE IS THE LORA SEND STRING------------\n");
		printf("Wrote %d bytes: %s\n", len, buf);
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
	}
	/* Set the device in sleep state. */
	set_state(fd, LORA_STATE_SLEEP);
	printf("The LoRa device is in 0x%X state\n", get_state(fd));
	/* Close device node. */
	close(fd);
	return 0;
}
