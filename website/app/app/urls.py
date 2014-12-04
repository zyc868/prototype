from django.conf.urls import patterns, include, url
from django.contrib import admin

try:
    # Are we running on michael's dev machine?
    import michaels_machine

    urlpatterns = patterns('',
        # Route to the Django admin interface.
        url(r'^admin/', include(admin.site.urls)),

        # Route to the Microbug application.
        url(r'^', include("microbug.urls", namespace='microbug')),
    )

except ImportError:
    try:
        # Are we running on the dev server?
        import sparkslabs

        urlpatterns = patterns('',
            # Route to the Django admin interface.
            url(r'^admin/', include(admin.site.urls)),

            # Route to the Microbug application.
            url(r'^', include("microbug.urls", namespace='microbug')),
        )

    except ImportError:
        # No. Assume we're running on Paul's dev machine in standalone mode.



        urlpatterns = patterns('',
            # Route to the Django admin interface.
            url(r'^admin/', include(admin.site.urls)),

            # Route to the Microbug application.
            url(r'^microbug/', include("microbug.urls", namespace='microbug')),
        )
