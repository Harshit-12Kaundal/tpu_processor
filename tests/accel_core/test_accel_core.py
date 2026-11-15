import os
import numpy as np
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

N = int(os.environ.get("N", "4"))


async def reset(dut):
    dut.rst.value = 1
    dut.load_en.value = 0
    dut.w_flat.value = 0
    dut.a_flat.value = 0
    dut.relu_en.value = 0
    dut.shift.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0


async def run(dut, X, W, shift, relu):
    M = X.shape[0]
    dut.relu_en.value = int(relu)
    dut.shift.value = shift

    packed = 0
    for r in range(N):
        for c in range(N):
            packed |= (int(W[r][c]) & 0xFF) << ((r * N + c) * 8)
    dut.w_flat.value = packed
    dut.load_en.value = (1 << (N*N)) - 1
    await RisingEdge(dut.clk)
    dut.load_en.value = 0

    LAT = 2 * N - 1          # 2(N-1) for the matmul core, +1 for the activation register
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
async def random_pipeline(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    for i in range(20):
        await reset(dut)
        M = 2 * N
        X = np.random.randint(-128, 128, size=(M, N))
        W = np.random.randint(-128, 128, size=(N, N))
        shift = int(np.random.randint(0, 17))
        relu = bool(i % 2)
        Y = await run(dut, X, W, shift, relu)
        exp = golden(X, W, shift, relu)
        assert np.array_equal(Y, exp), f"shift={shift} relu={relu}\nX=\n{X}\nW=\n{W}\ngot=\n{Y}\nexp=\n{exp}"
    dut._log.info(f"accel_core N={N}: INT8 in, INT8 out, matches NumPy")


@cocotb.test()
async def corner_cases(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    for v in (-128, 127):
        for shift in (0, 8, 16):
            for relu in (False, True):
                await reset(dut)
                X = np.full((N, N), v)
                W = np.full((N, N), v)
                Y = await run(dut, X, W, shift, relu)
                exp = golden(X, W, shift, relu)
                assert np.array_equal(Y, exp), f"v={v} shift={shift} relu={relu}\ngot=\n{Y}\nexp=\n{exp}"
