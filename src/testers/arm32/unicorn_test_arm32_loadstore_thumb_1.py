#!/usr/bin/env python3
## -*- coding: utf-8 -*-

from __future__          import print_function
from triton              import *
from unicorn             import *
from unicorn.arm_const   import *

import pprint
import random
import sys

ADDR  = 0x100000
STACK = 0x200000
HEAP  = 0x300000
SIZE  = 5 * 1024 * 1024

CODE  = [
    # ADR -------------------------------------------------------------------- #
    (b"\x08\xa0", "adr r0, 0x20"),

    # LDM - Pre-indexed addressing ------------------------------------------- #
    (b"\x91\xe8\x3c\x00", "ldm r1, {r2, r3, r4, r5}"),

    # LDM - Post-indexed addressing ------------------------------------------ #
    (b"\x3c\xc9",         "ldm r1!, {r2, r3, r4, r5}"),

    # LDR - Offset addressing ------------------------------------------------ #
    (b"\x08\x68",         "ldr r0, [r1]"),
    (b"\x48\x68",         "ldr r0, [r1, #0x4]"),
    (b"\x51\xf8\x04\x0c", "ldr r0, [r1, #-0x4]"),

    # LDR - Pre-indexed addressing  ------------------------------------------ #
    (b"\x51\xf8\x00\x0f", "ldr r0, [r1]!"),
    (b"\x51\xf8\x04\x0f", "ldr r0, [r1, #0x4]!"),
    (b"\x51\xf8\x04\x0d", "ldr r0, [r1, #-0x4]!"),

    # LDR - Post-indexed addressing  ----------------------------------------- #
    (b"\x51\xf8\x04\x0b", "ldr r0, [r1], #0x4"),
    (b"\x51\xf8\x04\x09", "ldr r0, [r1], #-0x4"),

    # LDR with SP as operand ------------------------------------------------- #
    (b"\xd1\xf8\x00\xd0", "ldr sp, [r1]"),

    (b"\x00\x98",         "ldr r0, [sp]"),

    # LDRB - Offset addressing ----------------------------------------------- #
    (b"\x08\x78",         "ldrb r0, [r1]"),
    (b"\x08\x79",         "ldrb r0, [r1, #0x4]"),
    (b"\x11\xf8\x04\x0c", "ldrb r0, [r1, #-0x4]"),

    # LDRB - Pre-indexed addressing ------------------------------------------ #
    (b"\x11\xf8\x00\x0f", "ldrb r0, [r1]!"),
    (b"\x11\xf8\x04\x0f", "ldrb r0, [r1, #0x4]!"),
    (b"\x11\xf8\x04\x0d", "ldrb r0, [r1, #-0x4]!"),

    # LDRB - Post-indexed addressing ----------------------------------------- #
    (b"\x11\xf8\x04\x0b", "ldrb r0, [r1], #0x4"),
    (b"\x11\xf8\x04\x09", "ldrb r0, [r1], #-0x4"),

    # LDRD - Offset addressing ----------------------------------------------- #
    (b"\xd1\xe9\x00\x02", "ldrd r0, r2, [r1]"),
    (b"\xd1\xe9\x01\x02", "ldrd r0, r2, [r1, #0x4]"),
    (b"\x51\xe9\x01\x02", "ldrd r0, r2, [r1, #-0x4]"),

    # LDRD - Pre-indexed addressing ------------------------------------------ #
    (b"\xf1\xe9\x00\x02", "ldrd r0, r2, [r1]!"),
    (b"\xf1\xe9\x01\x02", "ldrd r0, r2, [r1, #0x4]!"),
    (b"\x71\xe9\x01\x02", "ldrd r0, r2, [r1, #-0x4]!"),

    # LDRD - Post-indexed addressing ----------------------------------------- #
    (b"\xf1\xe8\x01\x02", "ldrd r0, r2, [r1], #0x4"),
    (b"\x71\xe8\x01\x02", "ldrd r0, r2, [r1], #-0x4"),

    # STM - Pre-indexed addressing ------------------------------------------- #
    (b"\x81\xe8\x3c\x00", "stm r1, {r2, r3, r4, r5}"),

    # STM - Post-indexed addressing ------------------------------------------- #
    (b"\x3c\xc1",         "stm r1!, {r2, r3, r4, r5}"),

    # STR - Offset addressing ------------------------------------------------ #
    (b"\x08\x60",         "str r0, [r1]"),
    (b"\x48\x60",         "str r0, [r1, #0x4]"),
    (b"\x41\xf8\x04\x0c", "str r0, [r1, #-0x4]"),

    # STR - Pre-indexed addressing ------------------------------------------- #
    (b"\x41\xf8\x00\x0f", "str r0, [r1]!"),
    (b"\x41\xf8\x04\x0f", "str r0, [r1, #0x4]!"),
    (b"\x41\xf8\x04\x0d", "str r0, [r1, #-0x4]!"),

    # STR - Post-indexed addressing  ----------------------------------------- #
    (b"\x41\xf8\x04\x0b", "str r0, [r1], #0x4"),
    (b"\x41\xf8\x04\x09", "str r0, [r1], #-0x4"),

    # STR with SP as operand
    (b"\xc1\xf8\x00\xd0", "str sp, [r1]"),

    (b"\x00\x90",         "str r0, [sp]"),

    # STRB - Offset addressing ------------------------------------------------ #
    (b"\x08\x70",         "strb r0, [r1]"),
    (b"\x08\x71",         "strb r0, [r1, #0x4]"),
    (b"\x01\xf8\x04\x0c", "strb r0, [r1, #-0x4]"),

    # STRB - Pre-indexed addressing ------------------------------------------- #
    (b"\x01\xf8\x00\x0f", "strb r0, [r1]!"),
    (b"\x01\xf8\x04\x0f", "strb r0, [r1, #0x4]!"),
    (b"\x01\xf8\x04\x0d", "strb r0, [r1, #-0x4]!"),

    # STRB - Post-indexed addressing  ----------------------------------------- #
    (b"\x01\xf8\x04\x0b", "strb r0, [r1], #0x4"),
    (b"\x01\xf8\x04\x09", "strb r0, [r1], #-0x4"),

    # STRD - Offset addressing ------------------------------------------------ #
    (b"\xc1\xe9\x00\x02", "strd r0, r2, [r1]"),
    (b"\xc1\xe9\x01\x02", "strd r0, r2, [r1, #0x4]"),
    (b"\x41\xe9\x01\x02", "strd r0, r2, [r1, #-0x4]"),

    # STRD - Pre-indexed addressing ------------------------------------------- #
    (b"\xe1\xe9\x00\x02", "strd r0, r2, [r1]!"),
    (b"\xe1\xe9\x01\x02", "strd r0, r2, [r1, #0x4]!"),
    (b"\x61\xe9\x01\x02", "strd r0, r2, [r1, #-0x4]!"),

    # STRD - Post-indexed addressing  ----------------------------------------- #
    (b"\xe1\xe8\x01\x02", "strd r0, r2, [r1], #0x4"),
    (b"\x61\xe8\x01\x02", "strd r0, r2, [r1], #-0x4"),

    # STRH - Offset addressing ----------------------------------------------- #
    (b"\x08\x80",         "strh r0, [r1]"),
    (b"\x88\x80",         "strh r0, [r1, #0x4]"),
    (b"\x21\xf8\x04\x0c", "strh r0, [r1, #-0x4]"),

    # STRH - Pre-indexed addressing ------------------------------------------ #
    (b"\x21\xf8\x00\x0f", "strh r0, [r1]!"),
    (b"\x21\xf8\x04\x0f", "strh r0, [r1, #0x4]!"),
    (b"\x21\xf8\x04\x0d", "strh r0, [r1, #-0x4]!"),

    # STRH - Post-indexed addressing  ---------------------------------------- #
    (b"\x21\xf8\x04\x0b", "strh r0, [r1], #0x4"),
    (b"\x21\xf8\x04\x09", "strh r0, [r1], #-0x4"),
]


def emu_with_unicorn(opcode, istate):
    # Initialize emulator in arm32 mode.
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)

    # Map memory for this emulation.
    mu.mem_map(ADDR, SIZE)

    # Write machine code to be emulated to memory.
    index = 0
    for op, _ in CODE:
        mu.mem_write(ADDR+index, op)
        index += len(op)

    # Retrieve APSR register value.
    apsr = mu.reg_read(UC_ARM_REG_APSR)
    nzcv = istate['n'] << 31 | istate['z'] << 30 | istate['c'] << 29 | istate['v'] << 28

    mu.mem_write(STACK,                bytes(istate['stack']))
    mu.mem_write(HEAP,                 bytes(istate['heap']))
    mu.reg_write(UC_ARM_REG_R0,        istate['r0'])
    mu.reg_write(UC_ARM_REG_R1,        istate['r1'])
    mu.reg_write(UC_ARM_REG_R2,        istate['r2'])
    mu.reg_write(UC_ARM_REG_R3,        istate['r3'])
    mu.reg_write(UC_ARM_REG_R4,        istate['r4'])
    mu.reg_write(UC_ARM_REG_R5,        istate['r5'])
    mu.reg_write(UC_ARM_REG_R6,        istate['r6'])
    mu.reg_write(UC_ARM_REG_R7,        istate['r7'])
    mu.reg_write(UC_ARM_REG_R8,        istate['r8'])
    mu.reg_write(UC_ARM_REG_R9,        istate['r9'])
    mu.reg_write(UC_ARM_REG_R10,       istate['r10'])
    mu.reg_write(UC_ARM_REG_R11,       istate['r11'])
    mu.reg_write(UC_ARM_REG_R12,       istate['r12'])
    mu.reg_write(UC_ARM_REG_SP,        istate['sp'])
    mu.reg_write(UC_ARM_REG_R14,       istate['r14'])
    mu.reg_write(UC_ARM_REG_PC,        istate['pc'])
    mu.reg_write(UC_ARM_REG_APSR,      apsr & 0x0fffffff | nzcv)

    # Emulate opcode.
    # NOTE: The +4 and count=1 is a trick so UC updates PC.
    mu.emu_start(istate['pc'] | 1, istate['pc'] + len(opcode) + 4, count=1) # NOTE: Enable Thumb mode by setting lsb of PC.

    ostate = {
        "stack": bytearray(mu.mem_read(STACK, 0x100)),
        "heap":  bytearray(mu.mem_read(HEAP, 0x100)),
        "r0":    mu.reg_read(UC_ARM_REG_R0),
        "r1":    mu.reg_read(UC_ARM_REG_R1),
        "r2":    mu.reg_read(UC_ARM_REG_R2),
        "r3":    mu.reg_read(UC_ARM_REG_R3),
        "r4":    mu.reg_read(UC_ARM_REG_R4),
        "r5":    mu.reg_read(UC_ARM_REG_R5),
        "r6":    mu.reg_read(UC_ARM_REG_R6),
        "r7":    mu.reg_read(UC_ARM_REG_R7),
        "r8":    mu.reg_read(UC_ARM_REG_R8),
        "r9":    mu.reg_read(UC_ARM_REG_R9),
        "r10":   mu.reg_read(UC_ARM_REG_R10),
        "r11":   mu.reg_read(UC_ARM_REG_R11),
        "r12":   mu.reg_read(UC_ARM_REG_R12),
        "sp":    mu.reg_read(UC_ARM_REG_SP),
        "r14":   mu.reg_read(UC_ARM_REG_R14),
        "pc":    mu.reg_read(UC_ARM_REG_PC),
        "n":   ((mu.reg_read(UC_ARM_REG_APSR) >> 31) & 1),
        "z":   ((mu.reg_read(UC_ARM_REG_APSR) >> 30) & 1),
        "c":   ((mu.reg_read(UC_ARM_REG_APSR) >> 29) & 1),
        "v":   ((mu.reg_read(UC_ARM_REG_APSR) >> 28) & 1),
    }
    return ostate


def emu_with_triton(opcode, istate):
    ctx = TritonContext()
    ctx.setArchitecture(ARCH.ARM32)

    inst = Instruction(opcode)
    inst.setAddress(istate['pc'])

    ctx.setConcreteMemoryAreaValue(STACK,           bytes(istate['stack']))
    ctx.setConcreteMemoryAreaValue(HEAP,            bytes(istate['heap']))
    ctx.setConcreteRegisterValue(ctx.registers.r0,  istate['r0'])
    ctx.setConcreteRegisterValue(ctx.registers.r1,  istate['r1'])
    ctx.setConcreteRegisterValue(ctx.registers.r2,  istate['r2'])
    ctx.setConcreteRegisterValue(ctx.registers.r3,  istate['r3'])
    ctx.setConcreteRegisterValue(ctx.registers.r4,  istate['r4'])
    ctx.setConcreteRegisterValue(ctx.registers.r5,  istate['r5'])
    ctx.setConcreteRegisterValue(ctx.registers.r6,  istate['r6'])
    ctx.setConcreteRegisterValue(ctx.registers.r7,  istate['r7'])
    ctx.setConcreteRegisterValue(ctx.registers.r8,  istate['r8'])
    ctx.setConcreteRegisterValue(ctx.registers.r9,  istate['r9'])
    ctx.setConcreteRegisterValue(ctx.registers.r10, istate['r10'])
    ctx.setConcreteRegisterValue(ctx.registers.r11, istate['r11'])
    ctx.setConcreteRegisterValue(ctx.registers.r12, istate['r12'])
    ctx.setConcreteRegisterValue(ctx.registers.sp,  istate['sp'])
    ctx.setConcreteRegisterValue(ctx.registers.r14, istate['r14'])
    ctx.setConcreteRegisterValue(ctx.registers.pc,  istate['pc'] | 1)  # NOTE: Enable Thumb mode by setting lsb of PC.
    ctx.setConcreteRegisterValue(ctx.registers.n,   istate['n'])
    ctx.setConcreteRegisterValue(ctx.registers.z,   istate['z'])
    ctx.setConcreteRegisterValue(ctx.registers.c,   istate['c'])
    ctx.setConcreteRegisterValue(ctx.registers.v,   istate['v'])

    ctx.processing(inst)

    # print()
    # print(inst)
    # for x in inst.getSymbolicExpressions():
    #    print(x)
    # print()

    ostate = {
        "stack": bytearray(ctx.getConcreteMemoryAreaValue(STACK, 0x100)),
        "heap":  bytearray(ctx.getConcreteMemoryAreaValue(HEAP, 0x100)),
        "r0":    ctx.getSymbolicRegisterValue(ctx.registers.r0),
        "r1":    ctx.getSymbolicRegisterValue(ctx.registers.r1),
        "r2":    ctx.getSymbolicRegisterValue(ctx.registers.r2),
        "r3":    ctx.getSymbolicRegisterValue(ctx.registers.r3),
        "r4":    ctx.getSymbolicRegisterValue(ctx.registers.r4),
        "r5":    ctx.getSymbolicRegisterValue(ctx.registers.r5),
        "r6":    ctx.getSymbolicRegisterValue(ctx.registers.r6),
        "r7":    ctx.getSymbolicRegisterValue(ctx.registers.r7),
        "r8":    ctx.getSymbolicRegisterValue(ctx.registers.r8),
        "r9":    ctx.getSymbolicRegisterValue(ctx.registers.r9),
        "r10":   ctx.getSymbolicRegisterValue(ctx.registers.r10),
        "r11":   ctx.getSymbolicRegisterValue(ctx.registers.r11),
        "r12":   ctx.getSymbolicRegisterValue(ctx.registers.r12),
        "sp":    ctx.getSymbolicRegisterValue(ctx.registers.sp),
        "r14":   ctx.getSymbolicRegisterValue(ctx.registers.r14),
        "pc":    ctx.getSymbolicRegisterValue(ctx.registers.pc),
        "n":     ctx.getSymbolicRegisterValue(ctx.registers.n),
        "z":     ctx.getSymbolicRegisterValue(ctx.registers.z),
        "c":     ctx.getSymbolicRegisterValue(ctx.registers.c),
        "v":     ctx.getSymbolicRegisterValue(ctx.registers.v),
    }
    return ostate


def diff_state(state1, state2):
    for k, v in list(state1.items()):
        if (k == 'heap' or k == 'stack') and v != state2[k]:
            print('\t%s: (UC) != (TT)' %(k))
        elif not (k == 'heap' or k == 'stack') and v != state2[k]:
            print('\t%s: %#x (UC) != %#x (TT)' %(k, v, state2[k]))
    return


def print_state(istate, uc_ostate, tt_ostate):
    for k in sorted(istate.keys()):
        if k in ['stack', 'heap']:
            continue

        diff = "!=" if uc_ostate[k] != tt_ostate[k] else "=="

        print("{:>3s}: {:08x} | {:08x} {} {:08x}".format(k, istate[k], uc_ostate[k], diff, tt_ostate[k]))


def diff_heap(istate, uc_ostate, tt_ostate):
    print("IN|UC|TT")
    for a, b, c in zip(istate['heap'], uc_ostate['heap'], tt_ostate['heap']):
        if a != b or a != c:
            print("{:02x}|{:02x}|{:02x}".format(a, b, c), sep=" ")


def diff_stack(istate, uc_ostate, tt_ostate):
    print("IN|UC|TT")
    sp = istate["sp"]
    for a, b, c in zip(istate['stack'], uc_ostate['stack'], tt_ostate['stack']):
        if a != b or a != c:
            print("{:x}: {:02x}|{:02x}|{:02x}".format(sp, a, b, c), sep=" ")
        sp += 1


if __name__ == '__main__':
    # Initial state.
    state = {
        "stack": bytearray([255 - i for i in range(256)]),
        "heap":  bytearray([i for i in range(256)]),
        "r0":    0xdeadbeef,
        "r1":    HEAP + 10 * 4,
        "r2":    random.randint(0x0, 0xffffffff),
        "r3":    random.randint(0x0, 0xffffffff),
        "r4":    random.randint(0x0, 0xffffffff),
        "r5":    random.randint(0x0, 0xffffffff),
        "r6":    random.randint(0x0, 0xffffffff),
        "r7":    random.randint(0x0, 0xffffffff),
        "r8":    random.randint(0x0, 0xffffffff),
        "r9":    random.randint(0x0, 0xffffffff),
        "r10":   random.randint(0x0, 0xffffffff),
        "r11":   random.randint(0x0, 0xffffffff),
        "r12":   random.randint(0x0, 0xffffffff),
        "sp":    STACK,
        "r14":   random.randint(0x0, 0xffffffff),
        "pc":    ADDR,
        "n":     random.randint(0x0, 0x1),
        "z":     random.randint(0x0, 0x1),
        "c":     random.randint(0x0, 0x1),
        "v":     random.randint(0x0, 0x1),
    }

    # NOTE: This tests each instruction separately. Therefore, it keeps track of
    # PC and resets the initial state after testing each instruction.
    pc = ADDR
    for opcode, disassembly in CODE:
        try:
            state['pc'] = pc
            uc_state = emu_with_unicorn(opcode, state)
            tt_state = emu_with_triton(opcode, state)
            pc += len(opcode)
        except Exception as e:
            print('[KO] %s' %(disassembly))
            print('\t%s' %(e))
            sys.exit(-1)

        for a, b in zip(uc_state['heap'], tt_state['heap']):
            if a != b:
                print('[KO] %s (heap differs!)' %(disassembly))
                diff_heap(state, uc_state, tt_state)
                print_state(state, uc_state, tt_state)
                sys.exit(-1)

        for a, b in zip(uc_state['stack'], tt_state['stack']):
            if a != b:
                print('[KO] %s (stack differs!)' %(disassembly))
                diff_stack(state, uc_state, tt_state)
                print_state(state, uc_state, tt_state)
                sys.exit(-1)

        if uc_state != tt_state:
            print('[KO] %s' %(disassembly))
            diff_state(uc_state, tt_state)
            print_state(state, uc_state, tt_state)
            sys.exit(-1)

        print('[OK] %s' %(disassembly))

    sys.exit(0)
