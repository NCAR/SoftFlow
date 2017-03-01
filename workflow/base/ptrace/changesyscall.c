#include <sys/ptrace.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/user.h>
#include <sys/reg.h>
#include <sys/syscall.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 32bit
// EAX, e.g. execve = 0xb
// EBX, ECX, EDX, ESI, EDI, EBP

// 64bit
// RAX, e.g. execve = 0x3b
// RDI, RSI, RDX, R10, R8, R9

const int long_size = sizeof(long);

void reverse(char *str) 
{   int i, j;
    char temp;

    for(i = 0, j = strlen(str) - 2; i <= j; ++i, --j) {
        temp = str[i];
        str[i] = str[j];
        str[j] = temp;
    }
}

void getdata(pid_t child, long addr, char *str, int len)
{   char *laddr;
    int i, j;
    union u {
            long val;
            char chars[long_size];
    }data;
    
    i = 0;
    j = len / long_size;
    laddr = str;
    while(i < j) {
        data.val = ptrace(PTRACE_PEEKDATA, child, addr + i * 8, NULL);
        memcpy(laddr, data.chars, long_size);
        ++i;
        laddr += long_size;
    }
    
    j = len % long_size;
    if(j != 0) {
        data.val = ptrace(PTRACE_PEEKDATA, child, addr + i * 8, NULL);
        memcpy(laddr, data.chars, j);
    }
    str[len] = '\0';       
}

void putdata(pid_t child, long addr, char *str, int len)
{   char *laddr;
    int i, j;
    union u {
            long val;
            char chars[long_size];
    }data;
    
    i = 0;
    j = len / long_size;
    laddr = str;
    while(i < j) {
        memcpy(data.chars, laddr, long_size);
        ptrace(PTRACE_POKEDATA, child, addr + i * 8, data.val);
        ++i;
        laddr += long_size;
    }
    
    j = len % long_size;
    if(j != 0) {
        memcpy(data.chars, laddr, j);
        ptrace(PTRACE_POKEDATA, child, addr + i * 8, data.val);
    }
}

int main()
{   pid_t child;

    child = fork();
    if(child == 0) {
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        execl("/bin/ls", "ls", NULL);
    }
    else {
        long orig_rax;
        long params[6];
        int status;
        char *str, *laddr;
        int toggle = 0;
        
        while(1) {
            wait(&status);
            if(WIFEXITED(status))
                break;
            orig_rax = ptrace(PTRACE_PEEKUSER, child, 8 * ORIG_RAX, NULL);
           
            if(orig_rax == SYS_write) {
                if(toggle == 0) {
                    toggle = 1;
					// write (int __fd, __const void *__buf, size_t __n)
                    params[0] = ptrace(PTRACE_PEEKUSER, child, 8 * RDI, NULL);
                    params[1] = ptrace(PTRACE_PEEKUSER, child, 8 * RSI, NULL);
                    params[2] = ptrace(PTRACE_PEEKUSER, child, 8 * RDX, NULL);
                    params[3] = ptrace(PTRACE_PEEKUSER, child, 8 * R10, NULL);
                    params[4] = ptrace(PTRACE_PEEKUSER, child, 8 * R8, NULL);
                    params[5] = ptrace(PTRACE_PEEKUSER, child, 8 * R9, NULL);

                    str = (char *)calloc((params[2] + 1), sizeof(char));
                    getdata(child, params[1], str, params[2]);
                    //printf("BEFORE %ld, %s, %ld\n", params[0], str, params[2]);
                    reverse(str);
                    //printf("AFTER %ld, %s, %ld\n", params[0], str, params[2]);
                    putdata(child, params[1], str, params[2]);
                }
                else {
                    toggle = 0; 
                }
            }
            ptrace(PTRACE_SYSCALL, child, NULL, NULL);
        }
    }
    return 0;
}
