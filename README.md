# Numerical Conformal Bootstrap in 4D / 四维数值共形自举

<details open>
<summary>English</summary>

This repository was created as the final paper for the University of Chinese Academy of Sciences course **"Introduction to Conformal Field Theory"**. We gratefully acknowledge Prof. Xinan Zhou for his inspiring lectures.

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
</details>

<details>
<summary>中文</summary>

本仓库是中国科学院大学课程**《共形场论导论》**的期末课程论文，感谢周稀楠（Xinan Zhou）老师的精彩授课。

## 简介

本仓库提供了一个 Mathematica 实现，基于 Rattazzi 等人在论文[《Bounding scalar operator dimensions in 4D CFT》](https://arxiv.org/abs/0807.0004)中提出的数值共形自举方法。

共形自举是一种强大的非微扰工具，利用单性和交换对称性等基本原理，对理论中的算符谱($\Delta, l$)及 OPE 系数($\lambda$)提出普适约束。

本代码实现的算法可以给出另一标量算符 $\phi$（维度为 $d$）的 OPE 中最低维标量算符的上界 $f(d)$：
$$ \Delta_{\min} \le f(d) $$

## 方法概览

算法的核心步骤如下：
1.  **交换对称**：四点函数 $\langle\phi\phi\phi\phi\rangle$ 在算符互换下保持不变，由此得到约束方程；
2.  **求和规则**：结合交换对称方程和 OPE，可以得到一个必须满足的线性方程，即“求和规则”；
3.  **几何诠释**：将求和规则重新解释为几何问题：表示恒等算符的向量必须位于其他所有算符向量构成的凸锥中；
4.  **线性规划**：判断给定谱是否允许的过程转化为寻找“分离超平面”的问题，可通过线性规划高效求解。

## 代码说明（`Bootstrap4D.wl`）

主文件 `Bootstrap4D.wl` 对上述方法进行了完整且带注释的实现，其主要部分包括：
- **核心物理函数**：定义共形块（`g`、`k`）和求和规则函数（`F`），并提供 `computeDerivativeVector` 用于计算 `F` 的泰勒展开系数；
- **自举算法**：实现 `generateTrialSet` 生成测试向量集，以及利用 `LinearProgramming` 判断谱是否允许的 `isExcluded`；
- **高级接口**：提供 `FindBound`（单个 $d$ 的上界）和 `CalculateBoundCurve`（计算完整曲线）等易用函数；
- **示例与用法**：包含可运行示例，展示如何复现论文中的结果。

## 使用方法

### 先决条件
- 需要安装 Wolfram Mathematica。

### 步骤 1：单点计算
首先可以计算单个 $d$ 的上界。代码中给出了复现最简单上界 $f_2(d)$（仅使用二阶导数）的示例，取 $d=1.05$。

在 Mathematica 中打开 `Bootstrap4D.wl`，运行“示例 1”中的代码：
```mathematica
(* Example 1: Calculate the bound for a single point (d=1.05) using the 2D basis *)
Print["\n=== Example 1: Single Point Calculation (f_2(d)) ==="];
bound_f2_at_1p05 = FindBound[1.05, basis2D, paramsQuickTest];
Print["\nResult for f_2(1.05) ≈ ", bound_f2_at_1p05, " (Paper value ~2.989)"];
```
该示例运行速度较快，结果应接近 2.989。

### 步骤 2：计算完整曲线
可以计算并绘制完整的上界曲线。“示例 2”展示了如何获得 $f_2(d)$ 的曲线。

```mathematica
(* Example 2: Calculate and plot a full curve (f_2(d)) *)
Print["\n=== Example 2: Plotting the f_2(d) Curve ==="];
dValues_f2 = Range[1.01, 1.1, 0.01];
curveData_f2 = CalculateBoundCurve[dValues_f2, basis2D, paramsQuickTest];
ListLinePlot[curveData_f2, PlotLabel -> "Reproduced Simplest Bound f_2(d)"]```
**注意**：若使用更高维度的基（如 `basis9D`），计算会非常耗时，可能需要数小时乃至更久，具体取决于参数和硬件性能。

### 步骤 3：参数自定义
代码的参数配置十分灵活，可通过修改以下设置在精度和速度之间进行权衡：

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
调整这些值即可探索不同精度水平。

## 局限与未来工作
- **性能**：作为教学代码，本实现未针对高性能进行优化。若采用更先进的编程技巧，或将逻辑转写为 C++ 等编译语言，可显著提升速度；
- **渐近向量**：`computeAsymptoticVector` 目前只针对六阶导数基（`basis9D`）硬编码。若能推广到任意基，将是有价值的改进。

## 引用
若使用本工作，请引用原论文：
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
</details>
