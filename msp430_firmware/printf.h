/*
 *This is a printf.f file
 *It requires the following UART functions to be implemented in the code.
 *
 *This program is free software: you can redistribute it and/or modify
 *it under the terms of the GNU General Public License as published by
 *the Free Software Foundation, either version 3 of the License, or
 *(at your option) any later version.

 *This program is distributed in the hope that it will be useful,
 *but WITHOUT ANY WARRANTY; without even the implied warranty of
 *MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *GNU General Public License for more details.
 *
 *You should have received a copy of the GNU General Public License
 *along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *Parker Dillmann
 *www.longhornengineer.com
*/

/*
 *uart_printf(char*)
 *Converts and formats values to be sent via char UART. Works similar to normal printf function.
 *INPUT: Char* EX: uart_printf("DATA: %i\r\n", datvar);
 *RETURN: None
 */
void uart_printf(char *format, ...);
