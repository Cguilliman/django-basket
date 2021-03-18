if __name__ == "__main__":
    from setuptools import setup, find_packages

    pkj_name = 'django_basket'

    setup(
        name='django-ib-basket',
        version='0.2',
        long_description_content_type='text/x-rst',
        packages=[pkj_name] + [pkj_name + '.' + x for x in find_packages(pkj_name)],
        include_package_data=True,
    )
