#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

void strip_char(char *str, char strip)
{
    char *p, *q;
    for (q = p = str; *p; p++)
        if (*p != strip)
            *q++ = *p;
    *q = '\0';
}

int main(void) {
  char st[] ="1, 2   , 3";
  char *ch;
  printf("Split \"%s\"\n", st);
  ch = strtok(st, ",");
  while (ch != NULL) {
  //strip_char(ch, ' ');
  printf("%d\n", atoi(ch));
  printf("%s\n", ch);
  ch = strtok(NULL, ",");
  }
  return 0;
}
