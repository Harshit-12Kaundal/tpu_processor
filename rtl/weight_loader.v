module weight_loader #(parameter N = 4) (
    input  wire                clk,
    input  wire                rst,
    input  wire                cfg_we,
    input  wire [3:0]          cfg_addr,   // 2: write next weight byte, 3: reset pointer
    input  wire [7:0]          cfg_data,
    output wire [N*8-1:0]      w_rows,     // one private copy of the byte per PE row
    output reg  [N*N-1:0]      load_en
);
    localparam NW = N * N;
    localparam IW = $clog2(NW);
    reg [IW-1:0] idx;

    wire wr = cfg_we && (cfg_addr == 4'd2);

    always @(posedge clk) begin
        if (rst) begin
            idx     <= {IW{1'b0}};
            load_en <= {NW{1'b0}};
        end else begin
            load_en <= {NW{1'b0}};              // enables last one cycle
            if (wr) begin
                load_en[idx] <= 1'b1;
                if (idx == NW - 1) idx <= {IW{1'b0}};
                else               idx <= idx + 1'b1;
            end else if (cfg_we && cfg_addr == 4'd3) begin
                idx <= {IW{1'b0}};
            end
        end
    end

    genvar r;
    generate
        for (r = 0; r < N; r = r + 1) begin : g_row
            (* keep = "true" *) reg [7:0] wb;   // no reset needed: only used when load_en is set
            always @(posedge clk) if (wr) wb <= cfg_data;
            assign w_rows[r*8 +: 8] = wb;
        end
    endgenerate
endmodule
