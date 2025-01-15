---
# This is an odd section. Zola does not permit rendering a section with same name
# as a taxonomy. If both exist, the taxonomy will take precedence.
# At the same time, there is no good way to add extra data to a taxonomy term,
# other than loading extra metadata, etc.
# This section abuses the fact that sections do seem to coexist with taxonomies.
# In the taxonomy, we check if pa page in the right section exists, and if it
# does, we grab it. The taxonomy temp0late can then render page components as
# well as taxonomy components.
---
