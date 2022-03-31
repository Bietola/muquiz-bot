import sys
import subprocess
import threading
import atomics


CONTINUE = 1


def start(executable_file):
    return subprocess.Popen(
        executable_file,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


def read(process):
    return process.stdout.readline().decode("utf-8").strip()


def write(process, message):
    process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
    process.stdin.flush()


def terminate(process):
    process.stdin.close()
    process.terminate()
    process.wait(timeout=0.2)


def interact(
    process,
    stdout,
    stdin,
    interrupt_sig='INTERRUPT',
    log_interrupt=lambda msg: print(msg, file=sys.stderr)
):
    interrupt_cnt = atomics.atomic(width=4, atype=atomics.INT)
    # 0 means "keep going"
    interrupt_cnt.store(0)

    def loop(fun):
        while True:
            # Interrupt when interrupt_val is 1
            if interrupt_cnt.load() == 1:
                log_interrupt(f'Interrupting {process}')
                break

            fun()

    def w_interrupt_check(fun):
        res = fun()
        if res == interrupt_sig:
            # Setting this to 1 interrupts the thread
            interrupt_cnt.store(1)
            print(f'Interrupting {process}', file=sys.stderr)
        return res

    stdout_thread = threading.Thread(
        target=lambda: loop(lambda: stdout(read(process)))
    )

    stdin_thread = threading.Thread(
        target=lambda: loop(
            lambda: write(
                process,
                w_interrupt_check(stdin)
            )
        )
    )

    stdout_thread.start()
    stdin_thread.start()
    stdout_thread.join()
    stdin_thread.join()
