#=========================================================================
# setup.tcl
#=========================================================================
# This design-specific setup.tcl can overwrite any variable in the
# default innovus-flowsetup "setup.tcl" script

# Reduced-effort flow that sacrifices timing to iterate more quickly

set vars(reduced_effort_flow) false

# Should not be clock-gate aware since we are not clock gating

set vars(clock_gate_aware) false
