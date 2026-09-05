import Lake

open Lake DSL

package scaffold where
  version := v!"0.1.0"

-- Pin the mathlib tag that matches lean-toolchain.  Bump both together, never
-- one alone.
require "leanprover-community" / "mathlib" @ git "v4.33.1"

-- The formalisation lives under `formal/`, next to the blueprint that
-- documents it; the library root is `formal/Scaffold.lean`.
@[default_target]
lean_lib Scaffold where
  srcDir := "formal"
