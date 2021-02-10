#=========================================================================
# read-design.tcl
#=========================================================================
# Author : Alex Carsello
# Date   : September 28, 2020

# read_hdl -sv [lsort [glob -directory inputs -type f *.v *.sv]]

set a [open $dc_rtl_flist]
set lines [split [read $a] "\n"]
close $a;                          # Saves a few bytes :-)
foreach line $lines {
    if { [string match +incdir+* $line] } {
    #   lappend search_path [string range $line 8 end]
    #   puts $search_path
    } else {
      read_hdl -sv ./inputs/$line
    #   if { ![analyze -format sverilog ./inputs/$line] } { exit 1 }
    }
}

# Prevent backslashes from being prepended to signal names...
# this causes SAIF files to be invalid...needs to be before elaboration.

set_attribute hdl_array_naming_style %s_%d
set_attribute hdl_bus_wire_naming_style %s_%d
set_attribute bit_blasted_port_style %s_%d /

elaborate $design_name

