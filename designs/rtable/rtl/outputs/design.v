module rtable
//  #(parameter X = 4'd10,
//   parameter Y = 4'd10)
   (
    input [7:0]  dest_id,    //  destination ID - 7 bits long for max 10x10 = 100 nodes
    input clk,
    output reg [2:0] switch_port  //  switch port - N E W S and local directions for directional routing. only 3 bits for 5 possibilities
   );

   localparam NODES = 256;
   localparam X = 16;
   localparam Y = 16;

   // Those are direction codings that match the wiring indices
   // above. The router is configured to use those to select the
   // proper output port.
   localparam DIR_LOCAL = 3'b000;
   localparam DIR_NORTH = 3'b001;
   localparam DIR_EAST  = 3'b010;
   localparam DIR_SOUTH = 3'b011;
   localparam DIR_WEST  = 3'b100;

   localparam OUTPUTS = 3; //  3 bits per direction, 1 direction per node, so it's OUTPUTS*NODES bits

   wire [OUTPUTS*NODES-1:0] ROUTES = genroutes(7,8);

   always @(posedge clk)
   begin
      switch_port <= ROUTES[dest_id*OUTPUTS +: OUTPUTS]; // because the array is packed into a single linear array of bits, not 2D   
   end

   // Get the node number
   function integer nodenum(input integer x,input integer y);
      nodenum = x+y*X;
   endfunction // nodenum
   
   // This generates the lookup table for node at coord x,y
   function [NODES-1:0][2:0] genroutes(input integer x, input integer y);
      integer yd,xd;
      integer nd;
      reg [2:0] d;

      genroutes = {NODES{3'b000}};

      for (yd = 0; yd < Y; yd++) begin
         for (xd = 0; xd < X; xd++) begin : inner_loop
            nd = nodenum(xd,yd);
            d = 3'b111;
            if ((xd==x) && (yd==y)) begin
               d = DIR_LOCAL;
            end else if (xd==x) begin
               if (yd<y) begin
                  d = DIR_SOUTH;
               end else begin
                  d = DIR_NORTH;
               end
            end else begin
               if (xd<x) begin
                  d = DIR_WEST;
               end else begin
                  d = DIR_EAST;
               end
            end // else: !if(xd==x)
            genroutes[nd] = d;
//            $display("xd=%02d yd=%02d nd=%02d d=%02d", xd, yd, nd, d);
         end
      end
   endfunction


endmodule // mesh


