import RPi.GPIO as GPIO
from modules.adc.threads.adc_thread import AdcThread
from mqtt.core.conf import topic

import handlers
from .jobs.create_minute_sample_job import create_minute_sample_job
from .jobs.create_web_sample_job import create_web_sample_job
from .sensordict_wrapper import SensorDict_wrapper


def module_topics():
	topicpatterns = [
        topic("vmnengine/get/sensor/+", handlers.getSensorHandler, unpack=False),
	]

	return topicpatterns

def module_models():
	return { 'sensor_wrapper': SensorDict_wrapper(60) }

def module_jobs(schedule, **kwargs):
	minute_sample_job = create_minute_sample_job(**kwargs)
	web_sample_job = create_web_sample_job(**kwargs)

	schedule.every(60).seconds.do(minute_sample_job)
	schedule.every(7).seconds.do(web_sample_job)

def initialize_thread(get_next, event, **kwargs):
	thread = AdcThread(get_next(), 'adc', event, **kwargs)

	return thread

def module_must_unload(**kwargs):
	GPIO.cleanup()
