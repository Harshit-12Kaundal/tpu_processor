import os
import numpy as np
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

N = int(os.environ.get("N", "4"))


def to_signed32(v):
    return v - (1 << 32) if v & (1 << 31) else v


async def reset(dut):
    dut.rst.value = 1
    dut.load_en.value = 0
    dut.w_flat.value = 0
    dut.a_flat.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst.value = 0


async def matmul(dut, X, W):
    M = X.shape[0]

    packed = 0
    for r in range(N):
        for c in range(N):
            packed |= (int(W[r][c]) & 0xFF) << ((r * N + c) * 8)
    dut.w_flat.value = packed
    dut.load_en.value = (1 << (N*N)) - 1
    await RisingEdge(dut.clk)
    dut.load_en.value = 0

    Y = np.zeros((M, N), dtype=np.int64)
    for t in range(M + 2 * N):
        a_packed = 0
        if t < M:                                  # plain row, no skew in software
            for r in range(N):
                a_packed |= (int(X[t][r]) & 0xFF) << (r * 8)
        dut.a_flat.value = a_packed
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        bits = str(dut.y_flat.value)[::-1]   # LSB first; may hold x until data arrives
        for c in range(N):
            m = t - (N - 1) - c
            if 0 <= m < M:
                Y[m][c] = to_signed32(int(bits[c*32:(c+1)*32][::-1], 2))
    return Y


@cocotb.test()
async def random_matmul(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    for _ in range(10):
        await reset(dut)
        M = 2 * N
        X = np.random.randint(-128, 128, size=(M, N))
        W = np.random.randint(-128, 128, size=(N, N))
        Y = await matmul(dut, X, W)
        assert np.array_equal(Y, X @ W), f"X=\n{X}\nW=\n{W}\nY=\n{Y}\nexpected=\n{X @ W}"
    dut._log.info(f"skew + {N}x{N} array: matches NumPy with unskewed input")


@cocotb.test()
async def corner_cases(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    for v in (-128, 127):
        await reset(dut)
        X = np.full((N, N), v)
        W = np.full((N, N), v)
        Y = await matmul(dut, X, W)
        assert np.array_equal(Y, X @ W), f"corner {v}: got\n{Y}\nexpected\n{X @ W}"
