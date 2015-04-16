License
-------

  ![AGPL Logo](http://www.gnu.org/graphics/agplv3-155x51.png)
    
    Copyright © 2014,2015 Fundacja Nowoczesna Polska <fundacja@nowoczesnapolska.org.pl>
    
    For full list of contributors see AUTHORS section at the end. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    

Dependencies
============

 * Python >= 2.6
 * Django >= 1.5


Installation
============

1. Add 'ssify' to INSTALLES_APPS.
2. Add middleware classes:
   * ssify.middleware.SsifyMiddleware on top,
   * if using UpdateCacheMiddleware, add
     ssify.middleware.PrepareForCacheMiddleware after it,
   * ssify.middleware.LocaleMiddleware instead of stock LocaleMiddleware.
3. Make sure you have 'django.core.context_processors.request' in your
   TEMPLATE_CONTEXT_PROCESSORS.
4. Configure your webserver to use SSI ('ssi=on' with Nginx).

Usage
=====

1. Define your included urls using the @ssi_included decorator.
2. Define your ssi variables using the @ssi_variable decorator.
 

Authors
=======
 
* Radek Czajka <radekczajka@nowoczesnapolska.org.pl>

