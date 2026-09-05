import Scaffold.Results.Goldbach

/-!
# Regression tests

A `Tests/` module per `Results/` module.  Its job is to pin the *statements*,
not to prove anything new: if a definition is weakened or a hypothesis quietly
added, the build breaks here rather than silently in a downstream proof.

Every test is a closed `example` or an `#check` of an exact type, so the file
has no axioms of its own and adds nothing to the trusted base.
-/

namespace Scaffold
namespace Tests

-- The public statement of Lemma `small:lem`, pinned verbatim.
example : ∀ n : ℕ, 4 ≤ n → n ≤ 12 → Even n → IsGoldbachNumber n :=
  Results.goldbach_small

-- The bound of Lemma `lower:lem` is stated for every `n`, with no evenness
-- hypothesis; that is deliberate and is relied on above.
example : ∀ n : ℕ, IsGoldbachNumber n → 4 ≤ n :=
  fun _ h => four_le_of_isGoldbachNumber h

-- Ordered pairs: `8` has two, and the definition must not quotient them.
example : IsGoldbachPair 8 3 5 := ⟨by norm_num, by norm_num, rfl⟩
example : IsGoldbachPair 8 5 3 := ⟨by norm_num, by norm_num, rfl⟩

-- The reflection form agrees with the pair form.
example : IsGoldbachNumber 12 := isGoldbachNumber_iff.2 ⟨5, by norm_num, by norm_num, by norm_num⟩

end Tests
end Scaffold
