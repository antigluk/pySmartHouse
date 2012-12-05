#ifndef MAIN_H
#define MAIN_H

/* System headers */
#include <msp430.h>
#include <string.h>

/*
 * Standard shortcuts preferred by humans
 */
typedef unsigned int uint;
#define TRUE 1
#define FALSE 0

// maximum length of a user-entered command
#define CMDLEN 12

/* Our global functions */
void serial_log(const char *str);

#endif /* MAIN_H */
