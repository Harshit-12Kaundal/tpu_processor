module systolic #(parameter N = 4) (
    input  wire                clk,
    input  wire                rst,
    input  wire [N*N-1:0]    load_en,
    input  wire [N*N*8-1:0]    w_flat,   // PE(r,c) weight at [(r*N+c)*8 +: 8]
    input  wire [N*8-1:0]      a_flat,   // row r activation at [r*8 +: 8]
    output wire [N*32-1:0]     y_flat    // column c result at [c*32 +: 32]
);
    wire signed [7:0]  a_w [0:N*N-1];    // a_out of PE(r,c)
    wire signed [31:0] p_w [0:N*N-1];    // psum_out of PE(r,c)

    genvar r, c;
    generate
        for (r = 0; r < N; r = r + 1) begin : g_row
            for (c = 0; c < N; c = c + 1) begin : g_col
                wire signed [7:0]  a_in_w;
                wire signed [31:0] p_in_w;

                if (c == 0) begin : g_left
                    assign a_in_w = a_flat[r*8 +: 8];
                end else begin : g_left_pe
                    assign a_in_w = a_w[r*N + c - 1];
                end

                if (r == 0) begin : g_top
                    assign p_in_w = 32'sd0;
                end else begin : g_top_pe
                    assign p_in_w = p_w[(r-1)*N + c];
                end

                pe u_pe (
                    .clk(clk), .rst(rst), .load_w(load_en[r*N + c]),
                    .w_in(w_flat[(r*N + c)*8 +: 8]),
                    .a_in(a_in_w),
                    .psum_in(p_in_w),
                    .a_out(a_w[r*N + c]),
                    .psum_out(p_w[r*N + c])
                );
            end
        end

        for (c = 0; c < N; c = c + 1) begin : g_out
            assign y_flat[c*32 +: 32] = p_w[(N-1)*N + c];
        end
    endgenerate
endmodule
