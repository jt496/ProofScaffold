import Scaffold.Basic

/-!
# The verified initial range

Lemma `small:lem` of `tex/results/02-verification.tex`: every even `n` with
`4 ≤ n ≤ 12` is a Goldbach number.  This is the part of Theorem `verify:thm`
that is checked by the kernel rather than by `tools/cpp/goldbach.cpp`; the
manuscript says so explicitly, and the blueprint records the correspondence.
-/

namespace Scaffold
namespace Results

/-- Lemma `small:lem`. -/
theorem goldbach_small (n : ℕ) (h4 : 4 ≤ n) (h12 : n ≤ 12) (hn : Even n) :
    IsGoldbachNumber n := by
  interval_cases n
  · exact ⟨2, 2, by norm_num, by norm_num, rfl⟩
  · exact absurd hn (by decide)
  · exact ⟨3, 3, by norm_num, by norm_num, rfl⟩
  · exact absurd hn (by decide)
  · exact ⟨3, 5, by norm_num, by norm_num, rfl⟩
  · exact absurd hn (by decide)
  · exact ⟨3, 7, by norm_num, by norm_num, rfl⟩
  · exact absurd hn (by decide)
  · exact ⟨5, 7, by norm_num, by norm_num, rfl⟩

end Results
end Scaffold
