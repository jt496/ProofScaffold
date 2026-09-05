import Mathlib

/-!
# Goldbach pairs

The definitions of `tex/results/00-introduction.tex` (Definition `pair:def`),
and the elementary bound of `tex/results/01-tools.tex` (Lemma `lower:lem`).

Every Lean name in this development is tied to a manuscript label in
`formal/BLUEPRINT.md`; add the row there in the same commit as the theorem.
-/

namespace Scaffold

/-- `(p, q)` is a **Goldbach pair** for `n` when `p` and `q` are prime and sum
to `n`.  Ordered, matching Definition `pair:def`: `(3, 5)` and `(5, 3)` are two
pairs for `8`. -/
def IsGoldbachPair (n p q : ℕ) : Prop := p.Prime ∧ q.Prime ∧ p + q = n

/-- `n` is a **Goldbach number** when it admits at least one Goldbach pair. -/
def IsGoldbachNumber (n : ℕ) : Prop := ∃ p q, IsGoldbachPair n p q

/-- Lemma `lower:lem`: every Goldbach number is at least `4`. -/
theorem four_le_of_isGoldbachNumber {n : ℕ} (h : IsGoldbachNumber n) : 4 ≤ n := by
  obtain ⟨p, q, hp, hq, rfl⟩ := h
  have hp2 := hp.two_le
  have hq2 := hq.two_le
  omega

/-- Lemma `reflect:lem`: `n` is a Goldbach number exactly when the reflection
`n - p` of some prime `p ≤ n` is again prime.  This is the form every
computation in `tools/` evaluates. -/
theorem isGoldbachNumber_iff {n : ℕ} :
    IsGoldbachNumber n ↔ ∃ p, p ≤ n ∧ p.Prime ∧ (n - p).Prime := by
  constructor
  · rintro ⟨p, q, hp, hq, rfl⟩
    exact ⟨p, by omega, hp, by simpa using hq⟩
  · rintro ⟨p, hpn, hp, hq⟩
    exact ⟨p, n - p, hp, hq, by omega⟩

end Scaffold
