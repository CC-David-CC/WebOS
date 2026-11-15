// Independent declared expectations around native Arc's strict per-coordinate
// full-sweep boundary. Each case belongs to a separate real authored plane.
const p=(x,y)=>({x,y}),near=dy=>({a:p(10,0),b:p(Math.sqrt(100-dy*dy),dy),c:p(0,0)});
export const arcCases=[
 {name:'identical',branch:'CIRCLE',role:null,data:{a:p(3,-3),b:p(3,-3),c:p(3,7)}},
 {name:'near-positive',branch:'CIRCLE',role:null,data:near(5e-7)},
 {name:'near-negative',branch:'CIRCLE',role:null,data:near(-5e-7)},
 {name:'below-threshold',branch:'CIRCLE',role:null,data:near(1e-6*(1-1e-6))},
 {name:'at-threshold',branch:'ARC',role:null,data:near(1e-6)},
 {name:'above-threshold',branch:'ARC',role:null,data:near(1e-6*(1+1e-6))},
 {name:'at-threshold-negative',branch:'ARC',role:null,data:near(-1e-6)},
 {name:'above-threshold-negative',branch:'ARC',role:null,data:near(-1e-6*(1+1e-6))},
 {name:'diagonal-full',branch:'CIRCLE',role:null,data:{a:p(Math.sqrt(50),Math.sqrt(50)),b:p(10*Math.cos(Math.PI/4+1.2e-7),10*Math.sin(Math.PI/4+1.2e-7)),c:p(0,0)}},
 {name:'diagonal-partial',branch:'ARC',role:null,data:{a:p(Math.sqrt(50),Math.sqrt(50)),b:p(10*Math.cos(Math.PI/4+1.5e-7),10*Math.sin(Math.PI/4+1.5e-7)),c:p(0,0)}},
 {name:'construction-full',branch:'CIRCLE',role:'construction',data:{a:p(3,-3),b:p(3,-3),c:p(3,7)}}
];
