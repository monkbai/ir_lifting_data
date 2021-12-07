# SoK: Demystifying Binary Lifters Through the Lens of Downstream Applications (IEEE S&P 2022 artifacts)


Artifact for **IEEE Security and Privacy 2022** paper: "SoK: Demystifying Binary Lifters Through the Lens of Downstream Applications".

Paper link: TBA

Zenodo link: [https://zenodo.org/record/5163174#.YQy6dEC-vb0](https://zenodo.org/record/5163174#.YQy6dEC-vb0)

## Lifters:

 * McSema: [https://github.com/lifting-bits/mcsema](https://github.com/lifting-bits/mcsema)
 * McSema<sup>0</sup>: McSema with all LLVM optimizations disabled  
 * RetDec: [https://github.com/avast/retdec](https://github.com/avast/retdec)
 * Mctoll: [https://github.com/microsoft/llvm-mctoll](https://github.com/microsoft/llvm-mctoll)
 * BinRec: [https://github.com/securesystemslab/BinRec](https://github.com/securesystemslab/BinRec)

## Downstream Application

 * Pointer Analysis: Static Value-Flow Analysis (SVF)  [https://github.com/SVF-tools/SVF](https://github.com/SVF-tools/SVF)
 * Discriminability Analysis: Neural Code Comprehension (NCC) [https://github.com/spcl/ncc](https://github.com/spcl/ncc)
 * Decompilation: retdec-decompiler (llvmir2hll) [https://github.com/avast/retdec/tree/master/src/llvmir2hll](https://github.com/avast/retdec/tree/master/src/llvmir2hll)

Please refer to [lifter-summary](https://github.com/monkbai/ir_lifting_data/blob/master/lifter-sm.pdf) for the patching & augmenting we made on these four lifters and more details about the downstream applications we leveraged.

## Datasets

### Pointer Analysis
 * Flow-sensitive tests provided in SVF [test suite](https://github.com/SVF-tools/Test-Suite/tree/master/test_cases_bc/fs_tests)
 * Testcases generated with EMI mutation [alias_test/alias_data.txt](https://github.com/monkbai/ir_lifting_data/blob/master/alias_test/alias_data.txt)

### Discriminability Analysis
 * We use the POJ_104 dataset used in NCC, the lifted LLVM IR can be download from [here](https://github.com/monkbai/ir_lifting_data/blob/master/ncc_data/ncc_data.txt)

### Decompilation
 * In total nine C programs in SPEC INT 2006 benchmark, the lifted IR can be download from [decompile_data/decom_data.txt](https://github.com/monkbai/ir_lifting_data/blob/master/decompile_data/decom_data.txt)

### Address Sanitizer 
We apply the Address Sanitizer on the IR lifted by McSema and RetDec and compare the results with the binary-only tool, [RetroWrite](https://github.com/HexHive/retrowrite).

 * We use the Juliet dataset used by RetroWrite [Juliet Test Suite for C/C++](https://samate.nist.gov/SRD/testsuite.php), the lifted IR and recompiled binaries can be found in [ASan_test/ASan_test_data.txt](https://github.com/monkbai/ir_lifting_data/blob/master/ASan_test/ASan_test_data.txt)

## Code and Data Structure

```bash
├── ASan_test          (Data used to compare with binary-only tool: RetroWrite)
├── Binary_Diffing     (Data used to compare with binary-only tool: DeepBinDiff)
├── aarch64            (Data of three downstream applications on ARM64 platform)
├── alias_test         (Data used for Pointer Analysis: SVF test suite)
├── correctness_check  (Scripts used to check correctness of lifted IR)
├── decompile_data     (Data used for Decompilation: SPEC INT 2006)
├── ncc_data           (Data used for Discriminability Analysis: POJ-104)
└── lifter-sm.pdf      (Supplementary Materials)
```


## Main Results

<img src="https://github.com/monkbai/ir_lifting_data/blob/master/main_results.png" width="682" height="328" />

For more detailed evaluation results, please at the [paper](https://github.com/monkbai/ir_lifting_data).
