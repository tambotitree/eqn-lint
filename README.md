# eqn-lint

🔬 *Lint for LaTeX math and physics papers*.  
It checks equations for **dimensional consistency** and **symbolic algebra consistency** using AI.  
Perfect for scientists, reviewers, and journals.  

---

## Features
- ✅ **Dimensional audits**: Verify SI dimensions across equations.
- ✅ **Symbolic audits**: Catch algebraic inconsistencies.
- ✅ Few-shot learning for smarter context inference.
- ✅ CLI tool for batch processing `.tex` files.

---

## Install
```bash
git clone https://github.com/YOURNAME/eqn-lint.git
cd eqn-lint
pip install -r requirements.txt

---

## 🔑 API Key Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
2.	Edit .env and paste your OpenAI API key:
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

---

## 🧪 Quick Test

A sample LaTeX paper (LambShiftGA.tex) is provided in test/.

🧹 Dry Run (preview equations):

python bin/dimensional_audit.py -f test/LambShiftGA.tex --dry-run

## 📐 Dimensional Audit:

python bin/dimensional_audit.py -f test/LambShiftGA.tex 

## 🧠 Symbolic Audit:

python bin/symbolic_audit.py -f test/LambShiftGA.tex

---
## eqn-lint.py

# Run all audits
python eqn-lint.py check -f test/LambShiftGA.tex

# Skip prose and units audits
python eqn-lint.py check -f test/LambShiftGA.tex --skip prose,units

# Create submission package
python eqn-lint.py package -f test/LambShiftGA.tex

# Rate the paper
python eqn-lint.py rate

# Show help
python eqn-lint.py help

---


## 🛠️ Run All Audits: `audit_all.py`

Run all available audits on your LaTeX paper in one go. This will sequentially execute:  
- 📐 Dimensional Audit  
- 🧠 Symbolic Audit  
- 👁 Opacity Audit  
- ⚖️ Units Audit  
- 📖 Citation Audit  
- 📝 Context Audit  

### 📦 Usage

```bash
python bin/audit_all.py -f test/LambShiftGA.tex

---

## 🕵️‍♂️ Opacity Audit

The opacity_audit.py tool scans LaTeX papers for undefined symbols in equations and their surrounding context.
It helps authors avoid “opaque” notation by identifying symbols, acronyms, or notations that are used but never explained.

✅ Features
	•	Detects undefined symbols in equations.
	•	Recognizes common physics notations and skips flagging them (e.g., $c$ for speed of light).
	•	Suggests clear definitions for missing symbols.
	•	CLI tool for easy batch processing.

🧪 Quick Example

Run an opacity audit on a LaTeX file:

python bin/opacity_audit.py -f test/LambShiftGA.tex

```
Sample Output:
--- Equation 3 ---
$r$
🔍 Opacity Check Result:
❌ UNDEFINED SYMBOLS: 

1. $I_{n\kappa}(k)$ appears in the equation but is not defined in the nearby text. Consider defining it.  
2. $P_{n\kappa}(r)$ and $Q_{n\kappa}(r)$ are missing definitions. Suggest: "Radial wave functions."  
3. $k$ is undefined. Suggest: "Wave number."  

--- Equation 6 ---
\begin{equation}
I_{n\kappa}(k) = \int_0^\infty dr \, ...
\end{equation}
🔍 Opacity Check Result:
✅ ALL SYMBOLS DEFINED: No undefined symbols found.
```

---

## 1️⃣ units_audit.py
	•	📏 What it does: Checks for unit consistency in equations and text (e.g., mixing SI with CGS units, or ambiguous custom units).
	•	✅ Flags:
	•	--check-consistency to verify all units are in a single system (SI, CGS, etc.)
	•	--flag-custom for author-defined units like “arb. units.”
	•	🧠 Few-shot would teach it that “eV” is valid, but “MeV/c^2” in a length equation isn’t.


## 📑 Citation Audit

Run a check to verify that all citations in your LaTeX file are defined in the bibliography and not fabricated.

🧹 Dry Run:
```bash
python bin/citation_audit.py -f test/LambShiftGA.tex --dry-run

🔍 Full Audit:

python bin/citation_audit.py -f test/LambShiftGA.tex

### Sample Output:
```
--- Citation 1 ---
\cite{Hestenes1990}
🔍 Citation Check Result:
✅ DEFINED: \cite{Hestenes1990} appears correctly.

--- Citation 4 ---
\cite{Schrodinger1930,Hestenes1990}
🔍 Citation Check Result:
✅ DEFINED: \cite{Schrodinger1930,Hestenes1990} appears correctly.
```
---

### 📝 `context_audit.py`
Checks if each citation’s surrounding text accurately reflects the cited work.

#### Example:
```bash
python bin/context_audit.py -f test/LambShiftGA.tex

---

📝 prose_audit.py

Checks for clarity, conciseness, and jargon in the prose of LaTeX papers. Highlights overly technical or verbose paragraphs and suggests simpler alternatives.

📖 What it does:
	•	✅ Flags dense “PhD-speak” and recommends plain-English rewrites.
	•	✅ Detects typos and formatting issues in text sections.
	•	✅ Skips LaTeX boilerplate (preambles, equations).
	•	✅ Provides a summary report of clear vs. unclear paragraphs.

🚀 Usage

python bin/prose_audit.py -f path/to/paper.tex

---


## CLI Flags

Flag|Description
----|-----------
-f FILE|Path to the LaTeX .tex file
-o FILE|Save results to a log file
--dry-run|Extract equations without calling OpenAI

## 📂 Directory Structure

eqn-lint/
├── bin/                     # CLI tools
│   ├── dimensional_audit.py
│   └── symbolic_audit.py
├── test/                    # Sample LaTeX paper
│   └── LambShiftGA.tex
├── .env.example             # Template for API key
├── LICENSE                  # MIT License
├── README.md
└── requirements.txt         # Python dependencies

## 🙏 Acknowledgements
	•	OpenAI for the GPT API
	•	Inspiration: lint tools for code, applied to equations
	•	Lamb Shift example from boundary hypothesis work

⸻

## 🤝 Contributing

Pull requests welcome! Please open an issue to discuss changes or improvements.

⸻

## 📜 License

This project is licensed under the MIT License. See LICENSE for details.


