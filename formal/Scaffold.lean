-- Library root.  Every module in formal/Scaffold/ is imported here, so that
-- `lake build` builds the whole development and nothing can be orphaned.
import Scaffold.Basic
import Scaffold.Results.Goldbach
import Scaffold.Tests.Goldbach
