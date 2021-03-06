# -*- coding: utf-8 -*-
# Copyright 2017 Hyperkernel Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import z3

import libirpy
from libirpy import util
from hv6py.base import BaseStruct, Struct, Map, Refcnt, Refcnt2


def _populate_enums():
    module = sys.modules[__name__]
    #print module
    #print "datatypes._populate_enums():module(current running module): ".format(module) 
    ctx = libirpy.newctx()
    print "datatypes._populate_enums():"
    import hv6py.kernel.impl as hv6
    hv6._init_metadata(ctx)
    for k, v in ctx.metadata.items():
        if isinstance(v, tuple) and v[0] == 'DICompositeType':
            if v[1].get('tag') == 'DW_TAG_enumeration_type':
                name = v[1].get('name')
                size = v[1].get('size')
                elements = v[1].get('elements')

                if name is None or size is None or elements is None:
                    continue

                setattr(module, name + '_t', z3.BitVecSort(size))
                enum = {}

                for element in ctx.metadata.get(elements):
                    element = ctx.metadata.get(element)
                    assert element[0] == 'DIEnumerator'
                    element_name = element[1].get('name')
                    element_value = element[1].get('value')
                    enum[element_name] = z3.BitVecVal(element_value, size)

                setattr(module, name, type(name, (), enum))
    



# These are populated from llvm metadata info
page_type_t = None
file_type_t = None
proc_state_t = None
intremap_state_t = None


# Fetch the enums from the llvm metadata and populate this module with their values
_populate_enums()


assert page_type_t is not None
assert file_type_t is not None
assert proc_state_t is not None

PAGE_SIZE = 4096

PCI_START = 0xa0000000
PCI_END = 0x100000000

NPAGE = 8192
NDMAPAGE = 512
NPROC = 64
#add service bound:MAX_SVC
MAX_SVC = 189
# NTSLICE
NOFILE = 16
NFILE = 128
NPCIDEV = 64
NINTREMAP = 8
NPCIPAGE = (PCI_END - PCI_START) / PAGE_SIZE


bool_t = z3.BoolSort()

size_t = z3.BitVecSort(64)
uint64_t = z3.BitVecSort(64)
uint32_t = z3.BitVecSort(32)
uint16_t = z3.BitVecSort(16)
uint8_t = z3.BitVecSort(8)


ssize_t = z3.BitVecSort(64)
int64_t = z3.BitVecSort(64)
int32_t = z3.BitVecSort(32)
int16_t = z3.BitVecSort(16)
int8_t = z3.BitVecSort(8)
int = int32_t


pn_t = z3.BitVecSort(64)
test_t = z3.BitVecSort(32)
dmapn_t = z3.BitVecSort(64)
fn_t = z3.BitVecSort(64)
fd_t = z3.BitVecSort(32)
pte_t = z3.BitVecSort(64)
dmar_pte_t = z3.BitVecSort(64)
pid_t = z3.BitVecSort(64)
esbid_t = z3.BitVecSort(64)
off_t = z3.BitVecSort(64)
devid_t = z3.BitVecSort(16)

uintptr_t = z3.BitVecSort(64)
physaddr_t = uintptr_t

INITPID = z3.BitVecVal(1, pid_t)

MAX_INT64 = z3.BitVecVal(2 ** 64 - 1, 64)
tU1=z3.BitVecSort(8)
tU2=z3.BitVecSort(16)#add:service type
tU4=z3.BitVecSort(32)#add:primitive type
tUTwo = z3.BitVecSort(2)
tI2 = z3.BitVecSort(16) #ack_err type (k5_reply)

#事件服务总线帧头类型和6级网络定义（3比特）
K5_H0 = 1 #0型帧，头部2个八字节；
K5_H1 = 2  #1型帧，头部3个八字节；
K5_N1 = 3  #1级网，头部4个八字节；
K5_N2 = 4  #2级网，头部5个八字节；
K5_N3 = 5  #3级网，头部6个八字节；
K5_N4 = 6  #4级网，头部7个八字节；
K5_N5 = 7  #5级网，头部8个八字节；
K5_N6 = 8  #6级网，头部9个八字节；

K5_CALL = 0 #服务原语：00：同步请求调用；
K5_REPLY = 1 #服务原语：01：异步应答；
K5_SEND = 2 #服务原语：10：异步发送；
K5_WAIT = 3 #服务原语：11：同步等待接收；

def FreshVA():
    idx1 = util.FreshBitVec('idx1', size_t)
    idx2 = util.FreshBitVec('idx2', size_t)
    idx3 = util.FreshBitVec('idx3', size_t)
    idx4 = util.FreshBitVec('idx4', size_t)
    return [idx1, idx2, idx3, idx4]


def BIT64(bit): return z3.BitVecVal(1 << bit, 64)
def has_bit(v, bit): return (v & bit) != 0


PTE_P = BIT64(0)                            # present
PTE_W = BIT64(1)                            # writable
PTE_U = BIT64(2)                            # user
PTE_PWT = BIT64(3)                          # write through
PTE_PCD = BIT64(4)                          # cache disable
PTE_A = BIT64(5)                            # accessed
PTE_D = BIT64(6)                            # dirty
PTE_PS = BIT64(7)                           # page size
PTE_G = BIT64(8)                            # global
PTE_AVL = BIT64(9) | BIT64(10) | BIT64(11)  # available for software use
PTE_NX = BIT64(63)                          # execute disable
PTE_PERM_MASK = PTE_P | PTE_W | PTE_U | PTE_PWT | PTE_PCD | PTE_AVL | PTE_NX

DMAR_PTE_R = BIT64(0)     # Read
DMAR_PTE_W = BIT64(1)     # Write
DMAR_PTE_SNP = BIT64(11)  # Snoop Behaviour
DMAR_PTE_TM = BIT64(62)   # Transient Mapping


DMAR_PTE_ADDR_SHIFT = z3.BitVecVal(12, uint64_t)
PTE_PFN_SHIFT = z3.BitVecVal(12, uint64_t)


PGTYPE_PAGE = z3.BitVecVal(0, uint64_t)
PGTYPE_PROC = z3.BitVecVal(1, uint64_t)
PGTYPE_PAGE_DESC = z3.BitVecVal(2, uint64_t)
PGTYPE_FILE_TABLE = z3.BitVecVal(3, uint64_t)
PGTYPE_DEVICES = z3.BitVecVal(4, uint64_t)
PGTYPE_PCIPAGE = z3.BitVecVal(5, uint64_t)
PGTYPE_IOMMU_FRAME = z3.BitVecVal(6, uint64_t)
PGTYPE_NONE = z3.BitVecVal(7, uint64_t)


NPAGES_PAGES = NPAGE
NPAGES_PROC_TABLE = 6
NPAGES_FILE_TABLE = 2
NPAGES_PAGE_DESC_TABLE = 64
NPAGES_DEVICES = 2


class PCI(Struct):
    owner = Map(devid_t, pid_t)
    page_table_root = Map(devid_t, pn_t)


class Vectors(Struct):
    owner = Map(uint8_t, pid_t)


class IO(Struct):
    owner = Map(uint16_t, pid_t)


class Intremap(Struct):
    state = Map(size_t, intremap_state_t)
    devid = Map(size_t, devid_t)
    vector = Map(size_t, uint8_t)


class Page(Struct):
    data = Map(pn_t, uint64_t, uint64_t)
    owner = Map(pn_t, pid_t)
    type = Map(pn_t, page_type_t)

    pgtable_pn = Map(pn_t, uint64_t, uint64_t)
    pgtable_perm = Map(pn_t, uint64_t, uint64_t)
    pgtable_type = Map(pn_t, uint64_t, uint64_t)

    pgtable_reverse_pn = Map(pn_t, pn_t)
    pgtable_reverse_idx = Map(pn_t, pn_t)


class DMAPage(Struct):
    owner = Map(pn_t, pid_t)
    type = Map(pn_t, page_type_t)


class PCIPage(Struct):
    owner = Map(pn_t, devid_t)
    valid = Map(pn_t, bool_t)


class Proc(Struct):
    state = Map(pid_t, proc_state_t)
    ppid = Map(pid_t, pid_t)
    killed = Map(pid_t, bool_t)

    ipc_from = Map(pid_t, pid_t)
    ipc_val = Map(pid_t, uint64_t)
    ipc_page = Map(pid_t, pn_t)
    ipc_size = Map(pid_t, size_t)
    ipc_fd = Map(pid_t, fd_t)

    ofile = Map(pid_t, fd_t, fn_t)

    nr_children = Refcnt(pid_t, pid_t, size_t, initial_offset=1)
    nr_fds = Refcnt(pid_t, fd_t, size_t)
    nr_pages = Refcnt(pid_t, pn_t, size_t)
    nr_dmapages = Refcnt(pid_t, pn_t, size_t)
    nr_devs = Refcnt(pid_t, devid_t, size_t)
    nr_ports = Refcnt(pid_t, uint16_t, size_t)
    nr_vectors = Refcnt(pid_t, uint8_t, size_t)
    nr_intremaps = Refcnt(pid_t, size_t, size_t)

    stack = Map(pid_t, pn_t)
    hvm = Map(pid_t, pn_t)
    page_table_root = Map(pid_t, pn_t)

    use_io_bitmap = Map(pid_t, bool_t)
    io_bitmap_a = Map(pid_t, pn_t)
    io_bitmap_b = Map(pid_t, pn_t)

    intr = Map(pid_t, uint64_t, uint64_t)

    tlbinv = Map(pid_t, bool_t)

class tk5_net(Struct):
    """docstring for tk5_net"""
    net_level=Map(tU1,tU1)
    cvt_level=Map(tU1,tU1)
    name_len=Map(tU4,tU4)
    dst_port=Map(tU4,tU4)
    src_port=Map(tU4,tU4)  

class tk5_ehn(Struct):
    dst_addr=Map(tU4,tU4)
    src_addr=Map(tU4,tU4)

class s_buf(Struct):
    """docstring for s_buf"""
    value = Map(tU4,tU4)
class body(Struct):
    value = Map(tU4,tU4)      
#add:Esb struct
class Esb(Struct):   
    head = Map(tU4,tU4)
    src_port = Map(esbid_t, esbid_t)
    dst_port = Map(esbid_t, esbid_t)
    service=Map(tU2,tU2)
    primitive=Map(tU4,tU4)
    val=Map(esbid_t,uint64_t)
    bodys = body()

class File(Struct):
    type = Map(fn_t, file_type_t)
    refcnt = Refcnt2(fn_t, (pid_t, fd_t), size_t)
    value = Map(fn_t, uint64_t)
    omode = Map(fn_t, uint64_t)
    offset = Map(fn_t, size_t)


"""
Global kernel state for specification
"""
class KernelState(BaseStruct):
    print "datatypes.KernelState:  entrying... datatypes.KernelState"
    pages_ptr_to_int = Map(uint64_t)
    proc_table_ptr_to_int = Map(uint64_t)
    esb_table_ptr_to_int = Map(uint64_t)        #/*new*/
    page_desc_table_ptr_to_int = Map(uint64_t)
    file_table_ptr_to_int = Map(uint64_t)
    devices_ptr_to_int = Map(uint64_t)
    dmapages_ptr_to_int = Map(uint64_t)

    procs = Proc()
    esbs=Esb()
    from_=tk5_net()
    to=tk5_net()

    ehn = tk5_ehn()
    s_bufs = s_buf()
    pages = Page()
    dmapages = DMAPage()
    files = File()
    pci = PCI()
    pcipages = PCIPage()
    vectors = Vectors()
    io = IO()
    intremaps = Intremap()

    current = Map(pid_t)
    current_esb=Esb()
    #s_buf = Map(tU4)
    iotlbinv = Map(bool_t)

    def flush_iotlb(self):
        self.iotlbinv = z3.BoolVal(True)

    def flush_tlb(self, pid):
        self.procs[pid].tlbinv = z3.BoolVal(True)


def state_to_dict(state, model):
    m = {
        'procs': {},
        'pages': {},
        'current': model.evaluate(state.current).as_long(),
    }
    for p in range(1, NPROC):
        m['procs'][p] = {
            'state': model.evaluate(state.procs[p].state).as_long(),
            # 'ppid': model.evaluate(state.procs[p].ppid).as_long(),
            'page_table_root': model.evaluate(state.procs[p].page_table_root).as_long(),
            # 'nr_pages': model.evaluate(state.procs[p].nr_pages()).as_long(),
        }
    for p in range(0, NPAGE):
        page = {
            'owner': model.evaluate(state.pages[p].owner).as_long(),
            'type': model.evaluate(state.pages[p].type).as_long(),
        }

        if not (0 < page['owner'] < NPAGE):
            continue

        data = {}
        for idx in range(512):
            if model.evaluate(state.pages[p].data(idx) & PTE_P == 0):
                continue
            data[idx] = {}
            data[idx]['val'] = model.evaluate(state.pages[p].data(idx)).as_long()
            data[idx]['resource'] = model.evaluate(state.pages[p].pgtable_pn(idx)).as_long()
            data[idx]['type'] = model.evaluate(state.pages[p].pgtable_type(idx)).as_long()

        page['data'] = data

        m['pages'][p] = page

    return m
