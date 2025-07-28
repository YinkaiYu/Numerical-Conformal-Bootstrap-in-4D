# Numerical Conformal Bootstrap in 4D
A Mathematica implementation of the method from R. Rattazzi et al. (arXiv:0807.0004)

## Introduction

This repository contains a Mathematica implementation of the numerical conformal bootstrap method described in the seminal paper ["Bounding scalar operator dimensions in 4D CFT"](https://arxiv.org/abs/0807.0004) by Rattazzi, Rychkov, Tonni, and Vichi.

The conformal bootstrap is a powerful, non-perturbative approach to studying Conformal Field Theories (CFTs). It uses the fundamental principles of unitarity and crossing symmetry to derive universal constraints on the spectrum of operators ($\Delta, l$) and OPE coefficients ($\lambda$) of a theory.

This code specifically implements the algorithm used to derive an upper bound $f(d)$ on the dimension $\Delta_{\min}$ of the lowest-dimension scalar operator appearing in the OPE of another scalar operator $\phi$ with dimension $d$. The bound takes the form:
$$ \Delta_{\min} \le f(d) $$

## The Method at a Glance

The core logic of the algorithm is as follows:
1.  **Crossing Symmetry**: The four-point function $\langle\phi\phi\phi\phi\rangle$ must be invariant under the exchange of operators. This leads to a constraint equation.
2.  **Sum Rule**: By combining the crossing symmetry equation with the Operator Product Expansion (OPE), one derives a "sum rule"—a linear equation that must be satisfied by the CFT data.
3.  **Geometric Interpretation**: The sum rule is reinterpreted as a geometric problem: a specific vector (representing the identity operator) must lie within a convex cone formed by vectors representing all other operators in the theory.
4.  **Linear Programming**: The problem of determining if a given operator spectrum is allowed is transformed into a search for a "separating hyperplane," which can be solved efficiently using linear programming.

## About the Code (`Bootstrap4D.wl`)

The main file `Bootstrap4D.wl` contains a complete, commented implementation of this method. It is structured into several logical parts:
- **Part 1: Core Physics Functions**: Defines the fundamental building blocks like the conformal blocks (`g`, `k`) and the sum rule function (`F`). It also contains the robust `computeDerivativeVector` function, which calculates the Taylor expansion coefficients of `F`.
- **Part 2: The Bootstrap Algorithm**: Implements the core logic, including the `generateTrialSet` function to create the set of test vectors and the `isExcluded` function which uses `LinearProgramming` to determine if a given spectrum is allowed or not.
- **Part 3: High-Level Functions**: Provides user-friendly functions like `FindBound` to find the bound for a single `d` and `CalculateBoundCurve` to generate data for a full plot.
- **Part 4: Examples & Usage**: Contains runnable examples that demonstrate how to use the code to reproduce results from the paper.

## How to Use

### Prerequisites
- A working installation of Wolfram Mathematica.

### Step 1: Running a Single Point Calculation
The easiest way to start is to calculate the bound for a single value of `d`. The code includes an example to reproduce the simplest bound ($f_2(d)$, using only 2nd-order derivatives) for $d=1.05$.

Open `Bootstrap4D.wl` in Mathematica and run the code under "Example 1".
```mathematica
(* Example 1: Calculate the bound for a single point (d=1.05) using the 2D basis *)
Print["\n=== Example 1: Single Point Calculation (f_2(d)) ==="];
bound_f2_at_1p05 = FindBound[1.05, basis2D, paramsQuickTest];
Print["\nResult for f_2(1.05) ≈ ", bound_f2_at_1p05, " (Paper value ~2.989)"];
```
This should run relatively quickly and return a value close to 2.989.

### Step 2: Calculating a Full Curve
You can easily calculate and plot an entire bound curve. "Example 2" shows how to do this for the $f_2(d)$ bound.

```mathematica
(* Example 2: Calculate and plot a full curve (f_2(d)) *)
Print["\n=== Example 2: Plotting the f_2(d) Curve ==="];
dValues_f2 = Range[1.01, 1.1, 0.01];
curveData_f2 = CalculateBoundCurve[dValues_f2, basis2D, paramsQuickTest];
ListLinePlot[curveData_f2, PlotLabel -> "Reproduced Simplest Bound f_2(d)"]```
**Warning**: Calculating curves with higher-dimensional bases (like `basis9D`) is extremely time-consuming and may take several hours or even days depending on the parameters and your hardware.

### Step 3: Customization
The code is designed to be easily configurable. You can change the precision and speed of the calculation by modifying the parameter sets:

```mathematica
paramsQuickTest = <|
    "lmax" -> 4,          (* Max spin in trial set *)
    "Δmax" -> 10,         (* Max dimension in trial set *)
    "δΔ" -> 0.5,          (* Sampling step for dimension *)
    "xmax" -> 5,          (* Max x = (Δ-l-2)/l for asymptotics *)
    "δx" -> 1.0,          (* Sampling step for x *)
    "epsilon" -> 10^-5,   (* LP constraint margin *)
    "numIterations" -> 6  (* Bisection search iterations *)
|>;
```
Simply change these values to explore different levels of precision.

## Limitations & Future Work
- **Performance**: This is a direct, educational implementation. It is not optimized for high performance. Significant speed-ups could be achieved with more advanced programming techniques or by porting the logic to a compiled language like C++.
- **Asymptotic Vector**: The `computeAsymptoticVector` function is currently hard-coded for the 6th-order derivative basis (`basis9D`). Generalizing this for arbitrary bases would be a valuable extension.

## Citation
If you use this work, please cite the original paper:
```
@article{Rattazzi:2008pe,
    author = "Rattazzi, Riccardo and Rychkov, Vyacheslav S. and Tonni, Erik and Vichi, Alessandro",
    title = "{Bounding scalar operator dimensions in 4D CFT}",
    eprint = "0807.0004",
    archivePrefix = "arXiv",
    primaryClass = "hep-th",
    doi = "10.1088/1126-6708/2008/12/031",
    journal = "JHEP",
    volume = "12",
    pages = "031",
    year = "2008"
}
```