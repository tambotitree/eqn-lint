# lib/_fewshots.py

class FewShotLibrary:
    @staticmethod
    def citations():
        return [
            {"role": "system", "content": "You are an expert in LaTeX and academic citation checking."},
            {"role": "user", "content": "Check citations in: The well-known result \\cite{Einstein1905} changed physics."},
            {"role": "assistant", "content": "✅ DEFINED: \\cite{Einstein1905} appears correctly."},
            {"role": "user", "content": "Check citations in: A new method was proposed in \\cite{MissingRef}."},
            {"role": "assistant", "content": "❌ UNDEFINED: \\cite{MissingRef} is not defined in the bibliography."},
            {"role": "user", "content": "Check citations in: Smith et al. (2023) proposed this, but the DOI cannot be verified."},
            {"role": "assistant", "content": "⚠️ POSSIBLY FABRICATED: Smith et al. (2023) is not verifiable; double check."},
        ]

    @staticmethod
    def context():
        return [
            {"role": "system", "content": "You are an expert scientific reviewer. Audit citations for accuracy."},
            {"role": "user", "content": """Context:\n\u201cAs shown in \\cite{Hestenes1990}, the Zitterbewegung motion explains intrinsic spin.\u201d\nAudit:\nDoes \\cite{Hestenes1990} support this claim?"""},
            {"role": "assistant", "content": "✅ ACCURATE: The statement correctly reflects the findings in Hestenes1990."},
            {"role": "user", "content": """Context:\n\u201c\\cite{Hestenes1990} demonstrates faster-than-light particles exist.\u201d\nAudit:\nDoes \\cite{Hestenes1990} support this claim?"""},
            {"role": "assistant", "content": "❌ FABRICATION: Hestenes1990 does not claim faster-than-light particles exist."},
        ]

    @staticmethod
    def opacity():
        return [
            {"role": "system", "content": "You are an AI that reviews LaTeX papers for opaque or undefined symbols, acronyms, and notation."},
            {"role": "user", "content": """Check this equation:\n\\begin{equation}\n\\Delta G = \\Delta H - T \\Delta S\n\\end{equation}\nContext:\nThis is a standard Gibbs free energy equation. \\Delta H is the enthalpy change, \\Delta S is the entropy change, but T is used without explanation.\n\nOutput:\n❌ UNDEFINED SYMBOL: T appears in the equation but is not defined in the nearby text. Consider defining it as 'Temperature (K)'."""},
            {"role": "user", "content": """Check this equation:\n\\begin{equation}\nE = mc^2\n\\end{equation}\nContext:\nSpecial relativity: m is mass, c is speed of light, E is energy.\n\nOutput:\n✅ ALL SYMBOLS DEFINED: No undefined symbols found in nearby text."""},
        ]

    @staticmethod
    def symbols():
        return [
            {"role": "system", "content": "You are an expert in dimensional analysis and LaTeX math."},
            {"role": "user", "content": "Build a symbol dictionary for: E = mc^2"},
            {"role": "assistant", "content": """{
  \"E\": \"energy (J)\",
  \"m\": \"mass (kg)\",
  \"c\": \"speed of light (m/s)\"
}"""},
        ]

    @staticmethod
    def dimensions():
        return [
            {"role": "system", "content": "You are auditing LaTeX math for dimensional consistency."},
            {"role": "user", "content": """Check: E = mc^2\nSymbols:\n{
  \"E\": \"energy (J)\",
  \"m\": \"mass (kg)\",
  \"c\": \"speed of light (m/s)\"
}"""},
            {"role": "assistant", "content": "✅ CONSISTENT: [J] = [kg][m/s]^2 is dimensionally valid."},
        ]

    @staticmethod
    def units():
        return [
            {"role": "system", "content": "You are auditing LaTeX equations for unit system consistency and detecting non-standard units."},
            {"role": "user", "content": """Check the units in: F = ma
Context: Newton's second law. All units are SI.
"""}, 
            {"role": "assistant", "content": "✅ CONSISTENT: All units are SI (Force in N, mass in kg, acceleration in m/s^2)."},
            {"role": "user", "content": """Check the units in: P = IV
Context: Electric power equation. Units: I in Amps, V in Volts, P in Watts.
"""}, 
            {"role": "assistant", "content": "✅ CONSISTENT: All units are SI."},
            {"role": "user", "content": """Check the units in: F = mg
Context: g = 32 ft/s^2
"""}, 
            {"role": "assistant", "content": "❌ INCONSISTENT: g uses Imperial units (ft/s^2) while the rest of the equation likely expects SI. Consider converting to m/s^2."},
            {"role": "user", "content": """Check the units in: E = hc/λ
Context: E in eV, h in J·s, c in m/s, λ in nm.
"""}, 
            {"role": "assistant", "content": "⚠️ MIXED UNITS: Energy is in eV and wavelength in nm, while Planck’s constant uses SI units. Consider converting to consistent units."},
   ]