
administrator login:
username: adf782r234w
password: 341h32fuewr7

please install all required python packages from requirements.txt, to get API calling working you have to:

brew install rabbitmq

brew services start rabbitmq

rabbit mq status - to check if its working

run rabbitmq in a different terminal 
celery acts as the background engine for off-loading work, so that time consuming work can be ran outside of your Flask app
ie. you can still use flask while celery is working in the background
