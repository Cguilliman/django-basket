# Copy default migrations
cp ./django_basket/tests/migrations/0001* ./django_basket/migrations/
# Run general tests
coverage run -m django test --settings=django_basket.tests.settings.settings django_basket.tests.base
# Run rest tests with default settings
coverage run -a -m django test --settings=django_basket.tests.settings.default_rest django_basket.tests.default_rest
# Copy dynamic basket migration
cp ./django_basket/tests/migrations/0002* ./django_basket/migrations/
# Run dynamic basket tests
coverage run -a -m django test --settings=django_basket.tests.settings.dynamic_settings django_basket.tests.dynamic
# Delete copied migrations
rm ./django_basket/migrations/0*
coverage combine
coverage report
coverage xml
#coverage html