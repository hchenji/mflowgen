#=========================================================================
# Integer Multiplier Fixed Latency RTL Model
#=========================================================================

from pymtl        import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define datapath and control unit here.
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from pclib.rtl    import Mux, Reg, RegEn, RegRst
from pclib.rtl    import RightLogicalShifter, LeftLogicalShifter, Adder

#=========================================================================
# Constants
#=========================================================================

A_MUX_SEL_NBITS      = 1
A_MUX_SEL_LSH        = 0
A_MUX_SEL_LD         = 1
A_MUX_SEL_X          = 0

B_MUX_SEL_NBITS      = 1
B_MUX_SEL_RSH        = 0
B_MUX_SEL_LD         = 1
B_MUX_SEL_X          = 0

RESULT_MUX_SEL_NBITS = 1
RESULT_MUX_SEL_ADD   = 0
RESULT_MUX_SEL_0     = 1
RESULT_MUX_SEL_X     = 0

ADD_MUX_SEL_NBITS    = 1
ADD_MUX_SEL_ADD      = 0
ADD_MUX_SEL_RESULT   = 1
ADD_MUX_SEL_X        = 0

#=========================================================================
# Integer Multiplier Fixed-Latency Datapath
#=========================================================================

class IntMulBaseDpathRTL( Model ):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.req_msg_a      = InPort  (32)
    s.req_msg_b      = InPort  (32)
    s.resp_msg       = OutPort (32)

    # Control signals (ctrl -> dpath)

    s.a_mux_sel      = InPort  (A_MUX_SEL_NBITS)
    s.b_mux_sel      = InPort  (B_MUX_SEL_NBITS)
    s.result_mux_sel = InPort  (RESULT_MUX_SEL_NBITS)
    s.result_reg_en  = InPort  (1)
    s.add_mux_sel    = InPort  (ADD_MUX_SEL_NBITS)

    # Status signals (dpath -> ctrl)

    s.b_lsb          = OutPort (1)

    #---------------------------------------------------------------------
    # Struction composition
    #---------------------------------------------------------------------

    # B mux

    s.rshifter_out = Wire(32)

    s.b_mux = m = Mux( 32, 2 )
    s.connect_pairs(
      m.sel,                s.b_mux_sel,
      m.in_[B_MUX_SEL_RSH], s.rshifter_out,
      m.in_[B_MUX_SEL_LD],  s.req_msg_b,
    )

    # B register

    s.b_reg = m = Reg( 32 )
    s.connect_pairs(
      m.in_, s.b_mux.out,
    )

    # Right shifter

    s.rshifter = m = RightLogicalShifter(32)
    s.connect_pairs(
      m.in_,   s.b_reg.out,
      m.shamt, 1,
      m.out,   s.rshifter_out,
    )

    # A mux

    s.lshifter_out = Wire(32)

    s.a_mux = m = Mux( 32, 2 )
    s.connect_pairs(
      m.sel,                s.a_mux_sel,
      m.in_[A_MUX_SEL_LSH], s.lshifter_out,
      m.in_[A_MUX_SEL_LD],  s.req_msg_a,
    )

    # A register

    s.a_reg = m = Reg( 32 )
    s.connect_pairs(
      m.in_, s.a_mux.out,
    )

    # Left shifter

    s.lshifter = m = LeftLogicalShifter(32)
    s.connect_pairs(
      m.in_,   s.a_reg.out,
      m.shamt, 1,
      m.out,   s.lshifter_out,
    )

    # Result mux

    s.add_mux_out = Wire(32)

    s.result_mux = m = Mux( 32, 2 )
    s.connect_pairs(
      m.sel,                     s.result_mux_sel,
      m.in_[RESULT_MUX_SEL_ADD], s.add_mux_out,
      m.in_[RESULT_MUX_SEL_0],   0,
    )

    # Result register

    s.result_reg = m = RegEn(32)
    s.connect_pairs(
      m.en,  s.result_reg_en,
      m.in_, s.result_mux.out,
    )

    # Adder

    s.add = m = Adder(32)
    s.connect_pairs(
      m.in0, s.a_reg.out,
      m.in1, s.result_reg.out,
      m.cin, 0
    )

    # Add mux

    s.add_mux = m = Mux( 32, 2 )
    s.connect_pairs(
      m.sel,                     s.add_mux_sel,
      m.in_[ADD_MUX_SEL_ADD],    s.add.out,
      m.in_[ADD_MUX_SEL_RESULT], s.result_reg.out,
      m.out,                     s.add_mux_out,
    )

    # Status signals

    s.connect( s.b_lsb, s.b_reg.out[0] )

    # Connect to output port

    s.connect( s.resp_msg, s.result_reg.out )

#=========================================================================
# Integer Multiplier Fixed-Latency Control Unit
#=========================================================================

class IntMulBaseCtrlRTL( Model ):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.req_val        = InPort  (1)
    s.req_rdy        = OutPort (1)

    s.resp_val       = OutPort (1)
    s.resp_rdy       = InPort  (1)

    # Control signals (ctrl -> dpath)

    s.a_mux_sel      = OutPort (A_MUX_SEL_NBITS)
    s.b_mux_sel      = OutPort (B_MUX_SEL_NBITS)
    s.result_mux_sel = OutPort (RESULT_MUX_SEL_NBITS)
    s.result_reg_en  = OutPort (1)
    s.add_mux_sel    = OutPort (ADD_MUX_SEL_NBITS)

    # Status signals (dpath -> ctrl)

    s.b_lsb          = InPort  (1)

    #---------------------------------------------------------------------
    # State
    #---------------------------------------------------------------------

    s.STATE_NBITS = 2
    s.STATE_IDLE  = 0
    s.STATE_CALC  = 1
    s.STATE_DONE  = 2

    s.state = RegRst( s.STATE_NBITS, reset_value = s.STATE_IDLE )

    #---------------------------------------------------------------------
    # Counter
    #---------------------------------------------------------------------

    s.counter = RegRst( 6, reset_value = 31 )

    #---------------------------------------------------------------------
    # State Transitions
    #---------------------------------------------------------------------

    @s.combinational
    def state_transitions():

      curr_state = s.state.out
      next_state = s.state.out

      # Transistions out of IDLE state

      if ( s.state.out == s.STATE_IDLE ):
        if ( s.req_val and s.req_rdy ):
          next_state = s.STATE_CALC

      # Transistions out of CALC state

      if ( s.state.out == s.STATE_CALC ):
        if s.counter.out == 0:
          next_state = s.STATE_DONE

      # Transistions out of DONE state

      if ( s.state.out == s.STATE_DONE ):
        if ( s.resp_val and s.resp_rdy ):
          next_state = s.STATE_IDLE

      s.state.in_.value = next_state

    #---------------------------------------------------------------------
    # State Outputs
    #---------------------------------------------------------------------

    s.do_sh_add = Wire(1)
    s.do_sh     = Wire(1)

    @s.combinational
    def state_outputs():

      current_state = s.state.out

      # In IDLE state we simply wait for inputs to arrive and latch them

      if current_state == s.STATE_IDLE:

        s.req_rdy.value        = 1
        s.resp_val.value       = 0

        s.a_mux_sel.value      = A_MUX_SEL_LD
        s.b_mux_sel.value      = B_MUX_SEL_LD
        s.result_mux_sel.value = RESULT_MUX_SEL_0
        s.result_reg_en.value  = 1
        s.add_mux_sel.value    = ADD_MUX_SEL_X

        s.counter.in_.value    = 31

      # In CALC state we iteratively add/shift to caculate mult

      elif current_state == s.STATE_CALC:

        s.do_sh_add.value      = (s.b_lsb == 1) # do shift and add
        s.do_sh.value          = (s.b_lsb == 0) # do shift but no add

        s.req_rdy.value        = 0
        s.resp_val.value       = 0

        s.a_mux_sel.value      = A_MUX_SEL_LSH
        s.b_mux_sel.value      = B_MUX_SEL_RSH
        s.result_mux_sel.value = RESULT_MUX_SEL_ADD
        s.result_reg_en.value  = 1
        if s.do_sh_add:
          s.add_mux_sel.value  = ADD_MUX_SEL_ADD
        else:
          s.add_mux_sel.value  = ADD_MUX_SEL_RESULT

        s.counter.in_.value    = s.counter.out - 1

      # In DONE state we simply wait for output transition to occur

      elif current_state == s.STATE_DONE:

        s.req_rdy.value        = 0
        s.resp_val.value       = 1

        s.a_mux_sel.value      = A_MUX_SEL_X
        s.b_mux_sel.value      = B_MUX_SEL_X
        s.result_mux_sel.value = RESULT_MUX_SEL_X
        s.result_reg_en.value  = 0
        s.add_mux_sel.value    = ADD_MUX_SEL_X

        s.counter.in_.value    = 31

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

#=========================================================================
# Integer Multiplier Fixed Latency
#=========================================================================

class IntMulBasePRTL( Model ):

  # Constructor

  def __init__( s ):

    # Interface

    s.req    = InValRdyBundle  ( Bits(64) )
    s.resp   = OutValRdyBundle ( Bits(32) )

    # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Instantiate datapath and control models here and then connect them
    # together.
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    # Instantiate datapath and control

    s.dpath = IntMulBaseDpathRTL()
    s.ctrl  = IntMulBaseCtrlRTL()

    # Connect input interface to dpath/ctrl

    s.connect( s.req.msg[32:64],  s.dpath.req_msg_a  )
    s.connect( s.req.msg[ 0:32],  s.dpath.req_msg_b  )
    s.connect( s.req.val,         s.ctrl.req_val     )
    s.connect( s.req.rdy,         s.ctrl.req_rdy     )

    # Connect dpath/ctrl to output interface

    s.connect( s.dpath.resp_msg,  s.resp.msg         )
    s.connect( s.ctrl.resp_val,   s.resp.val         )
    s.connect( s.ctrl.resp_rdy,   s.resp.rdy         )

    # Connect status/control signals

    s.connect_auto( s.dpath, s.ctrl )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  # Line tracing

  def line_trace( s ):

    # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Add additional line tracing using the given line_trace_str for
    # internal state including the current FSM state.
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/
    #:
    #: line_trace_str = ""
    #:
    #: return "{}({}){}".format(
    #:   s.req,
    #:   line_trace_str,
    #:   s.resp,
    #: )
    #:

    if s.ctrl.state.out == s.ctrl.STATE_IDLE:
      line_trace_str = "I "

    elif s.ctrl.state.out == s.ctrl.STATE_CALC:
      if s.ctrl.do_sh_add:
        line_trace_str = "C+"
      elif s.ctrl.do_sh:
        line_trace_str = "C "
      else:
        line_trace_str = "C?"

    elif s.ctrl.state.out == s.ctrl.STATE_DONE:
      line_trace_str = "D "

    return "{}({} {} {} {}){}".format(
      s.req,
      s.dpath.a_reg.out,
      s.dpath.b_reg.out,
      s.dpath.result_reg.out,
      line_trace_str,
      s.resp
    )

