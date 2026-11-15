import os
import numpy as np
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

N = int(os.environ.get("N", "4"))


async def reset(dut):
    dut.rst.value = 1
    dut.cfg_we.value = 0
    dut.cfg_addr.value = 0
    dut.cfg_data.value = 0
    dut.a_flat.value = 0
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


async def load_weights(dut, W):
    await cfg(dut, 3, 0)                         # reset the weight pointer
    for r in range(N):
        for c in range(N):
            await cfg(dut, 2, int(W[r][c]) & 0xFF)
    await RisingEdge(dut.clk)                    # last PE captures its weight


async def run(dut, X, W, shift, relu):
    M = X.shape[0]
    await cfg(dut, 0, shift)
    await cfg(dut, 1, int(relu))
    await load_weights(dut, W)

    LAT = 2 * N - 1
    Y = np.zeros((M, N), dtype=np.int64)
    for t in range(M + LAT + 1):
        a_packed = 0
        if t < M:
            for r in range(N):
                a_packed |= (int(X[t][r]) & 0xFF) << (r * 8)
        dut.a_flat.value = a_packed
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        m = t - LAT
        if 0 <= m < M:
            out = int(dut.y_flat.value)
            for c in range(N):
                b = (out >> (c * 8)) & 0xFF
                Y[m][c] = b - 256 if b & 0x80 else b
    return Y


def golden(X, W, shift, relu):
    S = X.astype(np.int64) @ W.astype(np.int64)
    if relu:
        S = np.maximum(S, 0)
    return np.clip(S >> shift, -128, 127)


@cocotb.test()
async def serial_weights_pipeline(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset(dut)
    for i in range(10):
        M = 2 * N
        X = np.random.randint(-128, 128, size=(M, N))
        W = np.random.randint(-128, 128, size=(N, N))
        shift = int(np.random.randint(0, 17))
        relu = bool(i % 2)
        # no reset between rounds: checks that weights can be reloaded
        Y = await run(dut, X, W, shift, relu)
        exp = golden(X, W, shift, relu)
        assert np.array_equal(Y, exp), f"shift={shift} relu={relu}\nX=\n{X}\nW=\n{W}\ngot=\n{Y}\nexp=\n{exp}"
    dut._log.info(f"accel_top N={N}: serial weight load + core match NumPy")
