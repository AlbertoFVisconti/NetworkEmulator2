Maximize
 obj: lambda
Subject to
 o1: 10 lambda - i1 <= 0
 o2: 2 lambda - i2 <= 0
 o3: 15 lambda - i3 <= 0
 \ flow balance for real-value rate variables
 flow_r1_ri1: ri1_r2r1 - ri1_r1r2 + ri1_r3r1 - ri1_r1r3 + i1 = 0
 flow_r2_ri1: ri1_r1r2 - ri1_r2r1 + ri1_r3r2 - ri1_r2r3 + ri1_r4r2 - ri1_r2r4= 0
 flow_r3_ri1: ri1_r1r3 - ri1_r3r1 + ri1_r2r3 - ri1_r3r2 + ri1_r4r3 - ri1_r3r4= 0
 flow_r4_ri1: ri1_r2r4 - ri1_r4r2 + ri1_r3r4 - ri1_r4r3 - i1 = 0

 flow_r1_ri2: ri2_r2r1 - ri2_r1r2 + ri2_r3r1 - ri2_r1r3 - i2 = 0
 flow_r2_ri2: ri2_r1r2 - ri2_r2r1 + ri2_r3r2 - ri2_r2r3 + ri2_r4r2 - ri2_r2r4= 0
 flow_r3_ri2: ri2_r1r3 - ri2_r3r1 + ri2_r2r3 - ri2_r3r2 + ri2_r4r3 - ri2_r3r4= 0
 flow_r4_ri2: ri2_r2r4 - ri2_r4r2 + ri2_r3r4 - ri2_r4r3 + i2 = 0

 flow_r1_ri3: ri3_r2r1 - ri3_r1r2 + ri3_r3r1 - ri3_r1r3= 0
 flow_r2_ri3: ri3_r1r2 - ri3_r2r1 + ri3_r3r2 - ri3_r2r3 + ri3_r4r2 - ri3_r2r4= 0
 flow_r3_ri3: ri3_r1r3 - ri3_r3r1 + ri3_r2r3 - ri3_r3r2 + ri3_r4r3 - ri3_r3r4 + i3 = 0
 flow_r4_ri3: ri3_r2r4 - ri3_r4r2 + ri3_r3r4 - ri3_r4r3 - i3 = 0

 \ flow balance for indicators, for each flow, for each node
 flow_r1_i1: i1_r2r1 - i1_r1r2 + i1_r3r1 - i1_r1r3= -1
 flow_r2_i1: i1_r1r2 - i1_r2r1 + i1_r3r2 - i1_r2r3 + i1_r4r2 - i1_r2r4= 0
 flow_r3_i1: i1_r1r3 - i1_r3r1 + i1_r2r3 - i1_r3r2 + i1_r4r3 - i1_r3r4= 0
 flow_r4_i1: i1_r2r4 - i1_r4r2 + i1_r3r4 - i1_r4r3= 1

 flow_r1_i2: i2_r2r1 - i2_r1r2 + i2_r3r1 - i2_r1r3= 1
 flow_r2_i2: i2_r1r2 - i2_r2r1 + i2_r3r2 - i2_r2r3 + i2_r4r2 - i2_r2r4= 0
 flow_r3_i2: i2_r1r3 - i2_r3r1 + i2_r2r3 - i2_r3r2 + i2_r4r3 - i2_r3r4= 0
 flow_r4_i2: i2_r2r4 - i2_r4r2 + i2_r3r4 - i2_r4r3= -1

 flow_r1_i3: i3_r2r1 - i3_r1r2 + i3_r3r1 - i3_r1r3= 0
 flow_r2_i3: i3_r1r2 - i3_r2r1 + i3_r3r2 - i3_r2r3 + i3_r4r2 - i3_r2r4= 0
 flow_r3_i3: i3_r1r3 - i3_r3r1 + i3_r2r3 - i3_r3r2 + i3_r4r3 - i3_r3r4= -1
 flow_r4_i3: i3_r2r4 - i3_r4r2 + i3_r3r4 - i3_r4r3= 1

\ mutual exclusion of incoming into same node, for each flow, for each node
 in_r1_i1: i1_r2r1 + i1_r3r1 <= 1
 in_r2_i1: i1_r1r2 + i1_r3r2 + i1_r4r2 <= 1
 in_r3_i1: i1_r1r3 + i1_r2r3 + i1_r4r3 <= 1
 in_r4_i1: i1_r2r4 + i1_r3r4 <= 1

 in_r1_i2: i2_r2r1 + i2_r3r1 <= 1
 in_r2_i2: i2_r1r2 + i2_r3r2 + i2_r4r2 <= 1
 in_r3_i2: i2_r1r3 + i2_r2r3 + i2_r4r3 <= 1
 in_r4_i2: i2_r2r4 + i2_r3r4 <= 1

 in_r1_i3: i3_r2r1 + i3_r3r1 <= 1
 in_r2_i3: i3_r1r2 + i3_r3r2 + i3_r4r2 <= 1
 in_r3_i3: i3_r1r3 + i3_r2r3 + i3_r4r3 <= 1
 in_r4_i3: i3_r2r4 + i3_r3r4 <= 1

\ mutual exclusion of outgoing out of same node, for each flow, for each node
 out_r1_i1: i1_r1r2 + i1_r1r3 <= 1
 out_r2_i1: i1_r2r1 + i1_r2r3 + i1_r2r4 <= 1
 out_r3_i1: i1_r3r1 + i1_r3r2 + i1_r3r4 <= 1
 out_r4_i1: i1_r4r2 + i1_r4r3 <= 1

 out_r1_i2: i2_r1r2 + i2_r1r3 <= 1
 out_r2_i2: i2_r2r1 + i2_r2r3 + i2_r2r4 <= 1
 out_r3_i2: i2_r3r1 + i2_r3r2 + i2_r3r4 <= 1
 out_r4_i2: i2_r4r2 + i2_r4r3 <= 1

 out_r1_i3: i3_r1r2 + i3_r1r3 <= 1
 out_r2_i3: i3_r2r1 + i3_r2r3 + i3_r2r4 <= 1
 out_r3_i3: i3_r3r1 + i3_r3r2 + i3_r3r4 <= 1
 out_r4_i3: i3_r4r2 + i3_r4r3 <= 1

\ link capacities, for each link
 r1r2_c: ri1_r1r2 + ri1_r2r1 + ri2_r1r2 + ri2_r2r1 + ri3_r1r2 + ri3_r2r1<= 3
 r1r3_c: ri1_r1r3 + ri1_r3r1 + ri2_r1r3 + ri2_r3r1 + ri3_r1r3 + ri3_r3r1<= 10
 r2r3_c: ri1_r2r3 + ri1_r3r2 + ri2_r2r3 + ri2_r3r2 + ri3_r2r3 + ri3_r3r2<= 8
 r2r4_c: ri1_r2r4 + ri1_r4r2 + ri2_r2r4 + ri2_r4r2 + ri3_r2r4 + ri3_r4r2<= 10
 r3r4_c: ri1_r3r4 + ri1_r4r3 + ri2_r3r4 + ri2_r4r3 + ri3_r3r4 + ri3_r4r3<= 10
\ control of real-value flow variables by corresponding indicators, for each flow and link
 r1r2_ci1 : ri1_r1r2 - 3 i1_r1r2 <= 0
 r2r1_ci1 : ri1_r2r1 - 3 i1_r2r1 <= 0
 r1r3_ci1 : ri1_r1r3 - 10 i1_r1r3 <= 0
 r3r1_ci1 : ri1_r3r1 - 10 i1_r3r1 <= 0
 r2r3_ci1 : ri1_r2r3 - 8 i1_r2r3 <= 0
 r3r2_ci1 : ri1_r3r2 - 8 i1_r3r2 <= 0
 r2r4_ci1 : ri1_r2r4 - 10 i1_r2r4 <= 0
 r4r2_ci1 : ri1_r4r2 - 10 i1_r4r2 <= 0
 r3r4_ci1 : ri1_r3r4 - 10 i1_r3r4 <= 0
 r4r3_ci1 : ri1_r4r3 - 10 i1_r4r3 <= 0

 r1r2_ci2 : ri2_r1r2 - 3 i2_r1r2 <= 0
 r2r1_ci2 : ri2_r2r1 - 3 i2_r2r1 <= 0
 r1r3_ci2 : ri2_r1r3 - 10 i2_r1r3 <= 0
 r3r1_ci2 : ri2_r3r1 - 10 i2_r3r1 <= 0
 r2r3_ci2 : ri2_r2r3 - 8 i2_r2r3 <= 0
 r3r2_ci2 : ri2_r3r2 - 8 i2_r3r2 <= 0
 r2r4_ci2 : ri2_r2r4 - 10 i2_r2r4 <= 0
 r4r2_ci2 : ri2_r4r2 - 10 i2_r4r2 <= 0
 r3r4_ci2 : ri2_r3r4 - 10 i2_r3r4 <= 0
 r4r3_ci2 : ri2_r4r3 - 10 i2_r4r3 <= 0

 r1r2_ci3 : ri3_r1r2 - 3 i3_r1r2 <= 0
 r2r1_ci3 : ri3_r2r1 - 3 i3_r2r1 <= 0
 r1r3_ci3 : ri3_r1r3 - 10 i3_r1r3 <= 0
 r3r1_ci3 : ri3_r3r1 - 10 i3_r3r1 <= 0
 r2r3_ci3 : ri3_r2r3 - 8 i3_r2r3 <= 0
 r3r2_ci3 : ri3_r3r2 - 8 i3_r3r2 <= 0
 r2r4_ci3 : ri3_r2r4 - 10 i3_r2r4 <= 0
 r4r2_ci3 : ri3_r4r2 - 10 i3_r4r2 <= 0
 r3r4_ci3 : ri3_r3r4 - 10 i3_r3r4 <= 0
 r4r3_ci3 : ri3_r4r3 - 10 i3_r4r3 <= 0

\ bounds on the input variables
Bounds
 i1<=10
 i2<=2
 i3<=15

Binary
 i1_r1r2
 i1_r2r1
 i1_r1r3
 i1_r3r1
 i1_r2r3
 i1_r3r2
 i1_r2r4
 i1_r4r2
 i1_r3r4
 i1_r4r3

 i2_r1r2
 i2_r2r1
 i2_r1r3
 i2_r3r1
 i2_r2r3
 i2_r3r2
 i2_r2r4
 i2_r4r2
 i2_r3r4
 i2_r4r3

 i3_r1r2
 i3_r2r1
 i3_r1r3
 i3_r3r1
 i3_r2r3
 i3_r3r2
 i3_r2r4
 i3_r4r2
 i3_r3r4
 i3_r4r3

