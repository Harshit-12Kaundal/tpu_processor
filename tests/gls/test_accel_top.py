import os
import numpy as np
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

N = int(os.environ.get("N", "4"))
M = min(2 * N, 8)               # rows per run (buffer depth is 16)
ROUNDS = int(os.environ.get("ROUNDS", "10"))


async def reset(dut):
    dut.rst.value = 1
    dut.cfg_we.value = 0
    dut.cfg_re.value = 0
    dut.cfg_addr.value = 0
    dut.cfg_data.value = 0
    for _ in range(5):
        await RisingEdge(dut.clk)
    dut.rst.value = 0
    for _ in range(4):
        await RisingEdge(dut.clk)


async def cfg(dut, addr, data):
    dut.cfg_addr.value = addr
    dut.cfg_data.value = data
    dut.cfg_we.value = 1
    await RisingEdge(dut.clk)
    dut.cfg_we.value = 0


async def cfg_read(dut, addr):
    dut.cfg_addr.value = addr
    dut.cfg_re.value = 1
    await RisingEdge(dut.clk)
    dut.cfg_re.value = 0
    await Timer(300, unit="ns")
    return int(dut.cfg_rdata.value)


async def load_weights(dut, W):
    await cfg(dut, 3, 0)                         # reset the weight pointer
    for r in range(N):
        for c in range(N):
            await cfg(dut, 2, int(W[r][c]) & 0xFF)
    await RisingEdge(dut.clk)                    # last PE captures its weight


async def run(dut, X, W, shift, relu):
    await cfg(dut, 0, shift)
    await cfg(dut, 1, int(relu))
    await load_weights(dut, W)

    await cfg(dut, 5, 0)                         # reset buffer pointers
    for m in range(M):
        for r in range(N):
            await cfg(dut, 4, int(X[m][r]) & 0xFF)
    await cfg(dut, 6, M)                         # start

    for _ in range(M + 4 * N + 40):
        st = await cfg_read(dut, 8)
        if st & 1:
            break
    else:
        raise AssertionError("done flag never set")

    Y = np.zeros((M, N), dtype=np.int64)
    for m in range(M):
        for c in range(N):
            b = await cfg_read(dut, 7)
            Y[m][c] = b - 256 if b & 0x80 else b
    return Y


def golden(X, W, shift, relu):
    S = X.astype(np.int64) @ W.astype(np.int64)
    if relu:
        S = np.maximum(S, 0)
    return np.clip(S >> shift, -128, 127)


@cocotb.test()
async def buffered_pipeline(dut):
    cocotb.start_soon(Clock(dut.clk, 500, unit="ns").start())
    await reset(dut)
    for i in range(ROUNDS):
        X = np.random.randint(-128, 128, size=(M, N))
        W = np.random.randint(-128, 128, size=(N, N))
        shift = int(np.random.randint(0, 17))
        relu = bool(i % 2)
        # no reset between rounds: checks reloading and a second start
        Y = await run(dut, X, W, shift, relu)
        dut._log.info(f"round {i} simulated")
        exp = golden(X, W, shift, relu)
        assert np.array_equal(Y, exp), f"shift={shift} relu={relu}\nX=\n{X}\nW=\n{W}\ngot=\n{Y}\nexp=\n{exp}"
    dut._log.info(f"accel_top N={N}: host loads, starts, polls done, reads results; matches NumPy")
