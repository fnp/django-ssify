# Changelog

## 0.2.2 (2014-09-19)

* Return 404 from ssi_included views with unsupported languages.

* Set zip_safe=False, so egg loader middleware isn't required.


## 0.2.1 (2014-09-15)

* Fix packaging errors.


## 0.2 (2014-09-15)

* Nicer cache choosing: use settings.SSIFY_CACHE_ALIASES if set,
  otherwise use 'ssify' cache if configure, otherwise
  fall back to 'default'.

* Renamed `csrf_token` template tag to `ssi_csrf_token` to avoid
  simple mistakes.

* Cache control: `ssi_variable` now takes `patch_response` instead
  of `vary` parameter, `ssi_include` takes `timeout`, `version` and
  also `patch_reponse` parameters.  Also added some helper functions
  in ssify.utils.

* Added `flush_ssi_includes` function.

* Debug rendering: renamed SSIFY_DEBUG to SSIFY_RENDER, added support
  for including streaming responses when SSIFY_RENDER=True.

* Dropped Django 1.4 support.


## 0.1 (2014-09-02)

* Initial release.
