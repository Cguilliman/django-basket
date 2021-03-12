#coverage erase
coverage run -m django test --settings=django_basket.tests.settings
#coverage report
#coverage xml
coverage html