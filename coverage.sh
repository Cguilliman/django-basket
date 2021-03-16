#coverage erase
cp ./django_basket/tests/migrations/0001* ./django_basket/migrations/
coverage run -m django test --settings=django_basket.tests.settings django_basket.tests.base
cp ./django_basket/tests/migrations/0002* ./django_basket/migrations/
coverage run -a -m django test --settings=django_basket.tests.dynamic_settings django_basket.tests.dynamic
rm ./django_basket/migrations/0*
coverage combine
#coverage report
#coverage xml
coverage html