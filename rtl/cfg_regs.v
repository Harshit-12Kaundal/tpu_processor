module cfg_regs (
    input  wire       clk,
    input  wire       rst,
    input  wire       cfg_we,
    input  wire [3:0] cfg_addr,   // 0: shift, 1: relu_en
    input  wire [7:0] cfg_data,
    output wire       rst_core,
    output reg  [4:0] shift_q,
    output reg        relu_q
);
    reg [1:0] rst_sync;
    always @(posedge clk) rst_sync <= {rst_sync[0], rst};
    assign rst_core = rst_sync[1];

    always @(posedge clk) begin
        if (rst_core) begin
            shift_q <= 5'd0;
            relu_q  <= 1'b0;
        end else if (cfg_we) begin
            case (cfg_addr)
                4'd0: shift_q <= cfg_data[4:0];
                4'd1: relu_q  <= cfg_data[0];
                default: ;
            endcase
        end
    end
endmodule
