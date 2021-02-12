module simple
   (
    input a, b, clk,
    output reg y
   );

    always @(posedge clk) begin
        y <= a & b;
    end


endmodule


