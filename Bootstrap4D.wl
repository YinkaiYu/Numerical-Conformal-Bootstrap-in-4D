(* ==================================================================== *)
(* ==================================================================== *)
(*          Numerical Conformal Bootstrap in 4D - A Mathematica         *)
(*                     Implementation for R. Rattazzi et al. (0807.0004)  *)
(* ==================================================================== *)
(* ==================================================================== *)
(*
 * Author: Yin-Kai Yu
 * Date: July 2025
 *
 * Description:
 * This repository provides a Mathematica implementation of the numerical 
 * conformal bootstrap method described in the seminal paper "Bounding 
 * scalar operator dimensions in 4D CFT" by Rattazzi, Rychkov, Tonni, 
 * and Vichi.
 *
 * The code is structured into four main parts:
 * 1. Core Physics Functions: Definitions of conformal blocks and the sum rule function F.
 * 2. The Bootstrap Algorithm: The core logic for exclusion tests using Linear Programming.
 * 3. High-Level Functions: User-facing functions to calculate bounds and plot curves.
 * 4. Examples & Usage: Demonstrations of how to use the functions to reproduce results.
 *
 *)

ClearAll["Global`*"];
$HistoryLength = 0; (* Prevent memory issues during long runs *)


(* ==================================================================== *)
(* Part 1: Core Physics Functions                                      *)
(* ==================================================================== *)

(* Dolan-Osborn formula for 4D conformal blocks *)
k[β_, x_] := x^(β/2)*Hypergeometric2F1[β/2, β/2, β, x];
g[Δ_, l_, u_, v_] := Module[{z, zbar},
    {z, zbar} = {(1 + u - v + Sqrt[(1 + u - v)^2 - 4 u]) / 2, (1 + u - v - Sqrt[(1 + u - v)^2 - 4 u]) / 2};
    If[!FreeQ[{z, zbar}, Sqrt[_?(# < 0 &)]], Return[0]];
    If[z == zbar, Return[0]];
    (z*zbar)/(z - zbar)*(k[Δ + l, z] k[Δ - l - 2, zbar] - k[Δ + l, zbar] k[Δ - l - 2, z])
];

(* The Sum Rule function F *)
F[d_, Δ_, l_, z_, zbar_] := Module[{u, v},
  u = z*zbar;
  v = (1 - z)*(1 - zbar);
  (v^d*g[Δ, l, u, v] - u^d*g[Δ, l, v, u]) / (v^d - u^d)
];

(* The robust, memoized, numerical derivative computation module *)
computeDerivativeVector[d_?NumericQ, Δ_?NumericQ, l_?NumericQ, basis_] :=
  computeDerivativeVector[d, Δ, l, basis] = 
  Module[{Fexpr, series, poly, vec, maxOrder, p},
    Fexpr[a_, b_] := F[d, Δ, l, 1/2 + a + b, 1/2 + a - b];
    maxOrder = Max[Total /@ basis];
    series = Quiet@Series[Fexpr[a, b], {a, 0, maxOrder}, {b, 0, maxOrder}];
    poly = Expand[Normal[series]];
    vec = Table[p[[1]]! * p[[2]]! * Coefficient[Coefficient[poly, a, p[[1]]], b, p[[2]]], {p, basis}];
    Return[N[Chop[vec]]];
  ];


(* ==================================================================== *)
(* Part 2: The Bootstrap Algorithm                                     *)
(* ==================================================================== *)

(* Computes the asymptotic vector from Eq. (5.14) for a given basis. *)
(* NOTE: This formula is specific to 6th order derivatives. *)
computeAsymptoticVector[x_?NumericQ, basis_] := Module[{vec, p},
  vec = Table[If[2*p[[1]] + 2*p[[2]] == 6, 1/((2*p[[1]] + 1)*(2*p[[2]] + 1)*(1 + x)^(2*p[[2]])), 0], {p, basis}];
  Return[vec];
];

(* Generates the trial set of vectors for the linear programming problem. *)
generateTrialSet[d_?NumericQ, Δmin_?NumericQ, basis_, params_Association] := Module[
    {dToUse, vectors, lmax, Δmax, δΔ, xmax, δx},
    
    (* Unpack parameters *)
    {lmax, Δmax, δΔ, xmax, δx} = params[{"lmax", "Δmax", "δΔ", "xmax", "δx"}];
    
    dToUse = If[Abs[d - 1] < 10^-6, 1, d];
    
    vectors = {};
    
    (* Scalar operators *)
    For[Δ = Δmin, Δ <= Δmax, Δ += δΔ, 
        AppendTo[vectors, computeDerivativeVector[dToUse, Δ, 0, basis]];
    ];
    
    (* Higher spin operators *)
    For[l = 2, l <= lmax, l += 2, 
        For[Δ = l + 2, Δ <= Δmax, Δ += δΔ, 
            AppendTo[vectors, computeDerivativeVector[dToUse, Δ, l, basis]];
        ];
    ];
    
    (* Asymptotic vectors *)
    For[x = 0, x <= xmax, x += δx, 
        AppendTo[vectors, computeAsymptoticVector[x, basis]];
    ];
    
    Return[vectors];
];

(* The core exclusion function using Linear Programming *)
isExcluded[d_?NumericQ, Δmin_?NumericQ, basis_, params_Association] := Module[
    {vectors, constraints, solution, costVector, epsilon},
    
    epsilon = params["epsilon"];
    
    vectors = generateTrialSet[d, Δmin, basis, params];
    
    constraints = {vectors, ConstantArray[epsilon, Length[vectors]]};
    costVector = ConstantArray[0, Length[basis]];
    
    solution = Quiet@LinearProgramming[costVector, constraints[[1]], constraints[[2]]];
    Return[Head[solution] === List];
];


(* ==================================================================== *)
(* Part 3: High-Level Functions                                        *)
(* ==================================================================== *)

(* Finds the bound for a single value of d using a bisection search. *)
FindBound[d_?NumericQ, basis_, params_Association] := Module[
    {Δlower, Δupper, Δmid, numIterations},
    
    numIterations = params["numIterations"];
    {Δlower, Δupper} = {2.0, 4.0}; (* Initial search range *)
    
    Print["--- Starting Bootstrap for d = ", d, " ---"];
    
    For[i = 1, i <= numIterations, i++,
        Δmid = (Δlower + Δupper) / 2;
        Print["  Iteration ", i, "/", numIterations, ": Testing Δ_min = ", Round[Δmid, 0.001]];
        If[isExcluded[d, Δmid, basis, params],
            Print["    -> Excluded."]; Δupper = Δmid,
            Print["    -> Allowed."]; Δlower = Δmid
        ]
    ];
    
    Print["--- Finished Bootstrap for d = ", d, ". Bound found: ", Δupper, " ---"];
    Return[Δupper];
];

(* Calculates a list of points {d, f(d)} to plot the bound curve. *)
CalculateBoundCurve[dRange_, basis_, params_Association] := Module[{points},
    points = Table[
        {d, FindBound[d, basis, params]},
        {d, dRange}
    ];
    Return[points];
];


(* ==================================================================== *)
(* Part 4: Examples & Usage                                            *)
(* ==================================================================== *)

(* --- Define different sets of parameters for calculation quality --- *)
paramsQuickTest = <|
    "lmax" -> 4, "Δmax" -> 10, "δΔ" -> 0.5,
    "xmax" -> 5, "δx" -> 1.0, "epsilon" -> 10^-5, "numIterations" -> 6
|>;

paramsHighPrecision = <|
    "lmax" -> 10, "Δmax" -> 20, "δΔ" -> 0.2,
    "xmax" -> 10, "δx" -> 0.2, "epsilon" -> 10^-5, "numIterations" -> 8
|>;


(* --- Define the derivative bases --- *)
basis2D = {{2, 0}, {0, 2}};
basis9D = {{6, 0}, {4, 2}, {2, 4}, {0, 6}, {4, 0}, {2, 2}, {0, 4}, {2, 0}, {0, 2}};


(* --- Example 1: Calculate the bound for a single point (d=1.05) using the 2D basis --- *)
Print["\n=== Example 1: Single Point Calculation (f_2(d)) ==="];
bound_f2_at_1p05 = FindBound[1.05, basis2D, paramsQuickTest];
Print["\nResult for f_2(1.05) ≈ ", bound_f2_at_1p05, " (Paper value ~2.989)"];


(* --- Example 2: Calculate and plot a full curve (f_2(d)) --- *)
(* This is fast and can be run interactively. *)
Print["\n=== Example 2: Plotting the f_2(d) Curve ==="];
dValues_f2 = Range[1.01, 1.1, 0.01];
curveData_f2 = CalculateBoundCurve[dValues_f2, basis2D, paramsQuickTest];

plot_f2 = ListLinePlot[curveData_f2,
    PlotLabel -> "Reproduced Simplest Bound f_2(d)",
    AxesLabel -> {"d", "Δ_min bound"},
    GridLines -> Automatic,
    PlotStyle -> {Thick, Blue}
];
Print[plot_f2];


(* --- Example 3: Calculate a high-precision point from the paper (f_6(d)) --- *)
(* WARNING: This is computationally intensive and may take a very long time. *)
(* We calculate the bound for d=1.01. The paper's value is 2.207. *)
Print["\n=== Example 3: High-Precision Calculation for a Single Point (f_6(d)) ==="];
Print["WARNING: This will be very slow."];
(* bound_f6_at_1p01 = FindBound[1.01, basis9D, paramsHighPrecision]; *)
(* Print["\nResult for f_6(1.01) ≈ ", bound_f6_at_1p01, " (Paper value ~2.207)"]; *)
