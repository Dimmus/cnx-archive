-- ###
-- Copyright (c) 2013, Rice University
-- This software is subject to the provisions of the GNU Affero General
-- Public License version 3 (AGPLv3).
-- See LICENCE.txt for details.
-- ###
SELECT
  module_ident,
  %({0})s::text ||'-::-language' as key
FROM
  latest_modules
WHERE
  language ~ ('^'||req(%({0})s::text))
